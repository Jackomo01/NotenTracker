# main.py (Streamlit fix mit session_state)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- DATENBANK ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Jahr", "Schuljahr", "Fach", "Zeitpunkt", "Note"])

df = st.session_state.df
zeit_map = {"NSB1": 1, "HJ": 2, "NSB2": 3, "Z": 4}
zeit_reihenfolge = ["NSB1", "HJ", "NSB2", "Z"]
x_mapping = {zeit: i for i, zeit in enumerate(zeit_reihenfolge)}

# ---------------- HILFSFUNKTIONEN ----------------
def schuljahr_berechnen(jahr, zeitpunkt):
    if zeitpunkt in ["HJ", "NSB2", "Z"]:
        start = jahr - 1
        ende = jahr
    else:
        start = jahr
        ende = jahr + 1
    return f"{str(start)[-2:]}/{str(ende)[-2:]}"

def check_empty(df_check, msg="Keine Daten verfügbar"):
    if df_check.empty:
        st.warning(msg)
        return True
    return False

def alle_faecher(sj):
    filtered = df[df["Schuljahr"] == sj]
    if check_empty(filtered, f"Keine Daten für Schuljahr {sj}"):
        return pd.DataFrame()
    return filtered

# ---------------- NOTENEINGABE ----------------
def eingabe_note_ui():
    st.subheader("Note hinzufügen")
    jahr = st.number_input("Jahr", min_value=2000, max_value=2100, step=1, value=2026)
    fach = st.text_input("Fach").strip().capitalize()
    zeitpunkt = st.selectbox("Zeitpunkt", zeit_map.keys())
    note = st.slider("Note", 1.0, 6.0, 3.0, step=0.01)
    if st.button("Speichern"):
        schuljahr = schuljahr_berechnen(jahr, zeitpunkt)
        exist = df[
            (df["Schuljahr"] == schuljahr) &
            (df["Fach"] == fach) &
            (df["Zeitpunkt"] == zeitpunkt)
        ]
        if not exist.empty:
            df.loc[exist.index, "Note"] = note
            st.success(f"Note ersetzt: {fach} | {zeitpunkt} | {schuljahr} | {note}")
        else:
            df.loc[len(df)] = [jahr, schuljahr, fach, zeitpunkt, note]
            st.success(f"✔ Gespeichert: {fach} | {zeitpunkt} | {schuljahr} | {note}")
    # aktualisiere session_state
    st.session_state.df = df

# ---------------- NOTEN LÖSCHEN ----------------
def note_loeschen_ui():
    st.subheader("Note löschen")
    if df.empty:
        st.warning("Keine Noten vorhanden.")
        return
    sj = st.selectbox("Schuljahr wählen", df["Schuljahr"].unique())
    df_sj = df[df["Schuljahr"] == sj]
    fach = st.selectbox("Fach wählen", df_sj["Fach"].unique())
    df_fach = df_sj[df_sj["Fach"] == fach]
    note_index = st.selectbox(
        "Welche Note löschen?",
        df_fach.index,
        format_func=lambda i: f"{df_fach.loc[i,'Zeitpunkt']} | {df_fach.loc[i,'Note']}"
    )
    if st.button("Löschen"):
        df.drop(note_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        st.success("✔ Note erfolgreich gelöscht.")
    st.session_state.df = df

# ---------------- ANALYSEN ----------------
def durchschnitt_pro_fach_ui():
    sj = st.selectbox("Schuljahr wählen", df["Schuljahr"].unique())
    filtered = alle_faecher(sj)
    if filtered.empty: return
    result = filtered.groupby("Fach")["Note"].mean().round(2).reset_index()
    st.table(result)

def stabilitaet_ui():
    erk = st.checkbox("Erklärung anzeigen")
    if erk:
        st.info("Standardabweichung: klein = stabil, groß = schwankend")
    sj = st.selectbox("Schuljahr wählen", df["Schuljahr"].unique())
    filtered = alle_faecher(sj)
    if filtered.empty: return
    result = []
    for fach in filtered["Fach"].unique():
        fach_df = filtered[filtered["Fach"] == fach]
        if len(fach_df) < 2:
            val = "Nicht möglich (zu wenig Daten)"
        else:
            val = round(fach_df["Note"].std(), 2)
        result.append({"Fach": fach, "Stabilität": val})
    st.table(pd.DataFrame(result))

def jahresverbesserung_ui():
    sj = st.selectbox("Schuljahr wählen", df["Schuljahr"].unique())
    filtered = alle_faecher(sj)
    if filtered.empty: return
    result = []
    for fach in filtered["Fach"].unique():
        fach_df = filtered[filtered["Fach"]==fach].copy()
        fach_df["Zeit_num"] = fach_df["Zeitpunkt"].map(zeit_map)
        fach_df = fach_df.sort_values("Zeit_num")
        if len(fach_df) < 2:
            result.append({"Fach": fach, "Verbesserung": "Nicht möglich (zu wenig Daten)"})
            continue
        diff = fach_df.iloc[-1]["Note"] - fach_df.iloc[0]["Note"]
        status = "Besser" if diff < 0 else "Schlechter"
        result.append({"Fach": fach, "Verbesserung": f"{status} ({round(diff,2)})"})
    st.table(pd.DataFrame(result))

def entwicklung_alle_faecher_ui():
    sj = st.selectbox("Schuljahr wählen", df["Schuljahr"].unique())
    filtered = alle_faecher(sj)
    if filtered.empty: return
    plt.figure()
    for fach in filtered["Fach"].unique():
        fach_df = filtered[filtered["Fach"] == fach]
        vorhandene_zeiten = [zeit for zeit in zeit_reihenfolge if zeit in fach_df["Zeitpunkt"].values]
        if len(vorhandene_zeiten) < 2:
            y_werte = [fach_df[fach_df["Zeitpunkt"]==zeit]["Note"].iloc[0] for zeit in vorhandene_zeiten]
            x_werte = [x_mapping[zeit] for zeit in vorhandene_zeiten]
            plt.scatter(x_werte, y_werte, label=fach, marker="o")
            continue
        y_werte = [fach_df[fach_df["Zeitpunkt"]==zeit]["Note"].iloc[0] for zeit in vorhandene_zeiten]
        x_werte = [x_mapping[zeit] for zeit in vorhandene_zeiten]
        plt.plot(x_werte, y_werte, marker="o", linestyle="-", label=fach)
    plt.xticks(list(x_mapping.values()), list(x_mapping.keys()))
    plt.ylim(0.5, 6.5)
    plt.yticks([1,2,3,4,5,6])
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Note")
    plt.title(f"Notenentwicklung im Schuljahr {sj}")
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

def schuljahre_vergleichen_ui():
    sj1 = st.selectbox("Erstes Schuljahr", df["Schuljahr"].unique(), key="sj1")
    sj2 = st.selectbox("Zweites Schuljahr", df["Schuljahr"].unique(), key="sj2")
    df1 = df[df["Schuljahr"] == sj1]
    df2 = df[df["Schuljahr"] == sj2]
    if df1.empty and df2.empty:
        st.warning("Für beide Schuljahre existieren keine Noten.")
        return
    avg1 = df1.groupby("Fach")["Note"].mean().round(2) if not df1.empty else pd.Series()
    avg2 = df2.groupby("Fach")["Note"].mean().round(2) if not df2.empty else pd.Series()
    alle_faecher_set = sorted(set(avg1.index).union(set(avg2.index)))
    table = []
    for fach in alle_faecher_set:
        wert1 = avg1[fach] if fach in avg1 else "/"
        wert2 = avg2[fach] if fach in avg2 else "/"
        table.append({"Fach": fach, sj1: wert1, sj2: wert2})
    df_table = pd.DataFrame(table)
    st.table(df_table)

def schuljahre_diagramm_ui():
    if df.empty:
        st.warning("Keine Daten vorhanden.")
        return
    avg = df.groupby("Schuljahr")["Note"].mean().sort_index().round(2)
    plt.figure()
    plt.bar(avg.index, avg.values)
    plt.ylim(0.5, 6.5)
    plt.yticks([1,2,3,4,5,6])
    plt.xlabel("Schuljahr")
    plt.ylabel("Gesamtdurchschnitt (alle Fächer)")
    plt.title("Vergleich der Gesamtnote pro Schuljahr")
    plt.grid(axis="y")
    st.pyplot(plt)

# ---------------- STREAMLIT MENÜ ----------------
st.title("📊 Schulnoten Manager")

menu = st.sidebar.selectbox("Menü", ["Noten verwalten", "Analyse", "OCR Import"])

if menu == "Noten verwalten":
    sub = st.radio("Aktion", ["Note hinzufügen", "Note löschen"])
    if sub == "Note hinzufügen":
        eingabe_note_ui()
    else:
        note_loesch_
