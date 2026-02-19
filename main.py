import pandas as pd
import matplotlib.pyplot as plt
from dokument_import import dokument_import

# ---------------- DATENBANK ----------------
df = pd.DataFrame(columns=["Jahr", "Schuljahr", "Fach", "Zeitpunkt", "Note"])
zeit_map = {"NSB1": 1, "HJ": 2, "NSB2": 3, "Z": 4}

# ---------------- HILFSFUNKTIONEN ----------------
def print_header(title):
    print("\n" + "="*50)
    print(f"{title.upper()}")
    print("="*50)

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
        print(f"⚠️ {msg}")
        return True
    return False

def print_table(df_table, col1, col2):
    print("-"*50)
    for i, row in df_table.iterrows():
        print(f"{row[col1]} | {row[col2]}")
    print("-"*50)

def alle_faecher(sj):
    filtered = df[df["Schuljahr"] == sj]
    if check_empty(filtered, f"Keine Daten für Schuljahr {sj}"):
        return pd.DataFrame()
    return filtered

# ---------------- NOTENEINGABE ----------------
def eingabe_note():
    while True:
        try:
            jahr = int(input("Jahr eingeben (z.B. 2025): "))
        except:
            print("⚠️ Bitte eine ganze Zahl eingeben.")
            continue

        fach = input("Fach eingeben (z.B. Deutsch): ").strip().capitalize()
        zeitpunkt = input("Zeitpunkt (NSB1, HJ, NSB2, Z): ").strip().upper()
        if zeitpunkt not in zeit_map:
            print("⚠️ Ungültiger Zeitpunkt. Beispiel: NSB1")
            continue

        try:
            note = float(input("Note eingeben (z.B. 1.0): "))
        except:
            print("⚠️ Ungültige Note. Beispiel: 1.0")
            continue

        schuljahr = schuljahr_berechnen(jahr, zeitpunkt)

        exist = df[
            (df["Schuljahr"] == schuljahr) &
            (df["Fach"] == fach) &
            (df["Zeitpunkt"] == zeitpunkt)
        ]

        if not exist.empty:
            print("Eintrag existiert bereits.")
            ers = input("Ersetzen? (j/n): ").strip().lower()
            if ers == "j":
                df.loc[exist.index, "Note"] = note
                print("✔ Note ersetzt.")
                print("-"*50)
                print(f"✔ Gespeichert: {fach} | {zeitpunkt} | {schuljahr} | {note}")
                print("-"*50)
        else:
            df.loc[len(df)] = [jahr, schuljahr, fach, zeitpunkt, note]
            print("-"*50)
            print(f"✔ Gespeichert: {fach} | {zeitpunkt} | {schuljahr} | {note}")
            print("-"*50)

        mehr = input("Weitere Note eingeben? (j/n): ").strip().lower()
        if mehr != "j":
            break

def note_loeschen():
    global df

    if df.empty:
        print("⚠️ Keine Noten vorhanden.")
        return

    print("\nVorhandene Schuljahre:")
    schuljahre = df["Schuljahr"].unique()

    for i, sj in enumerate(schuljahre, 1):
        print(f"{i} - {sj}")

    eingabe = input("Schuljahr wählen (Nummer oder z.B. 25/26): ").strip()

    if eingabe.isdigit():
        try:
            sj = schuljahre[int(eingabe) - 1]
        except:
            print("⚠️ Ungültige Auswahl.")
            return
    else:
        if eingabe in schuljahre:
            sj = eingabe
        else:
            print("⚠️ Schuljahr existiert nicht.")
            return

    df_sj = df[df["Schuljahr"] == sj]

    print("\nFächer:")
    faecher = df_sj["Fach"].unique()

    for i, fach in enumerate(faecher, 1):
        print(f"{i} - {fach}")

    try:
        fach_index = int(input("Fach wählen (Nummer): ")) - 1
        fach = faecher[fach_index]
    except:
        print("⚠️ Ungültige Auswahl.")
        return

    df_fach = df_sj[df_sj["Fach"] == fach]

    print("\nNoten:")
    for i, (_, row) in enumerate(df_fach.iterrows(), 1):
        print(f"{i} - {row['Zeitpunkt']} | {row['Note']}")

    try:
        note_index = int(input("Welche Note löschen? ")) - 1
        index_to_drop = df_fach.index[note_index]
    except:
        print("⚠️ Ungültige Auswahl.")
        return

    df.drop(index_to_drop, inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("✔ Note erfolgreich gelöscht.")

# ---------------- ANALYSEN ----------------
def durchschnitt_pro_fach():
    sj = input("Schuljahr eingeben (z.B. 25/26): ").strip()
    filtered = alle_faecher(sj)
    if filtered.empty: return
    result = filtered.groupby("Fach")["Note"].mean().round(2).reset_index()
    print_table(result, "Fach", "Note")

def stabilitaet():
    erk = input("Erklärung anzeigen? (j/n): ").lower()
    if erk == "j":
        print("Standardabweichung: klein = stabil, groß = schwankend")
    sj = input("Schuljahr eingeben (z.B. 25/26): ").strip()
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
    print_table(pd.DataFrame(result), "Fach", "Stabilität")

def jahresverbesserung():
    sj = input("Schuljahr eingeben (z.B. 25/26): ").strip()
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
    print_table(pd.DataFrame(result), "Fach", "Verbesserung")


def entwicklung_alle_faecher():
    sj = input("Schuljahr eingeben (z.B. 25/26): ").strip()

    filtered = df[df["Schuljahr"] == sj]

    if filtered.empty:
        print(f"⚠️ Keine Daten für Schuljahr {sj}")
        return

    zeit_reihenfolge = ["NSB1", "HJ", "NSB2", "Z"]
    x_mapping = {zeit: i for i, zeit in enumerate(zeit_reihenfolge)}  # NSB1->0, HJ->1, ...

    plotted = False
    plt.figure()

    for fach in filtered["Fach"].unique():
        fach_df = filtered[filtered["Fach"] == fach]

        # nur vorhandene Punkte
        vorhandene_zeiten = [zeit for zeit in zeit_reihenfolge if zeit in fach_df["Zeitpunkt"].values]

        if len(vorhandene_zeiten) < 2:
            # Linie nicht möglich, aber Punkte anzeigen
            y_werte = [fach_df[fach_df["Zeitpunkt"]==zeit]["Note"].iloc[0] for zeit in vorhandene_zeiten]
            x_werte = [x_mapping[zeit] for zeit in vorhandene_zeiten]
            plt.scatter(x_werte, y_werte, label=fach, marker="o")
            continue

        # y- und x-Werte für Linie
        y_werte = [fach_df[fach_df["Zeitpunkt"]==zeit]["Note"].iloc[0] for zeit in vorhandene_zeiten]
        x_werte = [x_mapping[zeit] for zeit in vorhandene_zeiten]

        # Linie zwischen den vorhandenen Punkten
        plt.plot(x_werte, y_werte, marker="o", linestyle="-", label=fach)

        plotted = True

    # X-Achse vollständig beschriften
    plt.xticks(list(x_mapping.values()), list(x_mapping.keys()))
    plt.ylim(0.5, 6.5)
    plt.yticks([1,2,3,4,5,6])
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Note")
    plt.title(f"Notenentwicklung im Schuljahr {sj}")  # <-- hier war der Fehler
    plt.grid(True)
    plt.legend()
    plt.show()


def schuljahre_vergleichen():
    sj1 = input("Erstes Schuljahr eingeben (z.B. 25/26): ").strip()
    sj2 = input("Zweites Schuljahr eingeben (z.B. 26/27): ").strip()

    df1 = df[df["Schuljahr"] == sj1]
    df2 = df[df["Schuljahr"] == sj2]

    if df1.empty and df2.empty:
        print("⚠️ Für beide Schuljahre existieren keine Noten.")
        return

    avg1 = df1.groupby("Fach")["Note"].mean().round(2) if not df1.empty else pd.Series()
    avg2 = df2.groupby("Fach")["Note"].mean().round(2) if not df2.empty else pd.Series()

    alle_faecher = sorted(set(avg1.index).union(set(avg2.index)))

    def farbe(note):
        if note == "/":
            return "/"
        if note <= 2:
            return f"{note}"
        elif note <= 4:
            return f"{note}"
        else:
            return f"{note}"

    print("\n" + "="*60)
    print("VERGLEICH DER SCHULJAHRE – FACHDURCHSCHNITT")
    print("="*60)

    print(f"{'Fach':<18}{sj1:^18}{sj2:^18}")
    print("-"*60)

    for fach in alle_faecher:
        wert1 = avg1[fach] if fach in avg1 else "/"
        wert2 = avg2[fach] if fach in avg2 else "/"

        wert1_f = farbe(wert1) if wert1 != "/" else "/"
        wert2_f = farbe(wert2) if wert2 != "/" else "/"

        print(f"{fach:<18}{wert1_f:^18}{wert2_f:^18}")

    print("-"*60)

    ges1 = round(avg1.mean(), 2) if not avg1.empty else "/"
    ges2 = round(avg2.mean(), 2) if not avg2.empty else "/"

    ges1_f = farbe(ges1) if ges1 != "/" else "/"
    ges2_f = farbe(ges2) if ges2 != "/" else "/"

    print(f"{'Ø Gesamt':<18}{ges1_f:^18}{ges2_f:^18}")
    print("="*60)

def schuljahre_diagramm():
    if df.empty:
        print("⚠️ Keine Daten vorhanden.")
        return

    avg = df.groupby("Schuljahr")["Note"].mean().sort_index().round(2)

    if avg.empty:
        print("⚠️ Keine Durchschnittsdaten verfügbar.")
        return

    plt.figure()
    plt.bar(avg.index, avg.values)
    plt.ylim(0.5, 6.5)
    plt.yticks([1,2,3,4,5,6])
    plt.xlabel("Schuljahr")
    plt.ylabel("Gesamtdurchschnitt (alle Fächer)")
    plt.title("Vergleich der Gesamtnote pro Schuljahr")
    plt.grid(axis="y")
    plt.show()

# ---------------- MENÜ ----------------
def noten_verwalten():
    while True:
        print_header("Noten verwalten")
        print("1 - Note hinzufügen")
        print("2 - Note löschen")
        print("3 - Dokument scannen / OCR importieren")
        print("0 - Zurück zum Hauptmenü")
        print("="*50)
        wahl = input("Wahl: ").strip()

        if wahl == "1":
            eingabe_note()
        elif wahl == "2":
            note_loeschen()
        elif wahl == "3":
            global df
            df = dokument_import()
        elif wahl == "0":
            break
        else:
            print("⚠️ Ungültige Eingabe!")

def analyse_menue():
    print_header("Analyse")
    print("1 - Durchschnitt pro Fach")
    print("2 - Stabilität pro Fach")
    print("3 - Jahresverbesserung pro Fach")
    print("4 - Entwicklung aller Fächer (Diagramm)")
    print("5 - Zwei Schuljahre vergleichen")
    print("6 - Schuljahre Diagramm")
    print("0 - Zurück zum Hauptmenü")
    print("="*50)

# ---------------- HAUPTMENÜ ----------------
def hauptmenue():
    print_header("Hauptmenü")
    print("1 - Noten verwalten")
    print("2 - Analyse")
    print("0 - Programm beenden")
    print("="*50)

# ---------------- HAUPTSCHLEIFE ----------------
while True:
    hauptmenue()
    wahl = input("Wahl: ").strip()

    if wahl == "1":
        noten_verwalten()
    elif wahl == "2":
        while True:
            analyse_menue()
            a = input("Wahl: ").strip()
            if a=="1": durchschnitt_pro_fach()
            elif a=="2": stabilitaet()
            elif a=="3": jahresverbesserung()
            elif a=="4": entwicklung_alle_faecher()
            elif a=="5": schuljahre_vergleichen()
            elif a=="6": schuljahre_diagramm()
            elif a=="0": break
            else: print("⚠️ Ungültige Eingabe!")
    elif wahl == "0":
        print("Programm beendet.")
        break
    else:
        print("⚠️ Ungültige Eingabe!")
