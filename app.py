import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import numpy as np

st.set_page_config(
    page_title="NotenTracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── STATE ───
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Jahr", "Schuljahr", "Fach", "Zeitpunkt", "Note"])
if "save_msg" not in st.session_state:
    st.session_state.save_msg = None

zeit_map = {"NSB1": 1, "HJ": 2, "NSB2": 3, "Z": 4}

# ─── HELPERS ───
def schuljahr_berechnen(jahr, zeitpunkt):
    if zeitpunkt in ["HJ", "NSB2", "Z"]:
        start, ende = jahr - 1, jahr
    else:
        start, ende = jahr, jahr + 1
    return f"{str(start)[-2:]}/{str(ende)[-2:]}"

def note_klasse(note):
    if note <= 2.0: return "note-green"
    if note <= 4.0: return "note-yellow"
    return "note-red"

def save_note(jahr, fach, zeitpunkt, note):
    schuljahr = schuljahr_berechnen(jahr, zeitpunkt)
    d = st.session_state.df
    exist = d[(d["Schuljahr"] == schuljahr) & (d["Fach"] == fach) & (d["Zeitpunkt"] == zeitpunkt)]
    if not exist.empty:
        st.session_state.df.loc[exist.index, "Note"] = note
        return schuljahr, True
    new_row = pd.DataFrame([{"Jahr": jahr, "Schuljahr": schuljahr, "Fach": fach, "Zeitpunkt": zeitpunkt, "Note": note}])
    # FIX 7: concat with copy=False to silence FutureWarning
    st.session_state.df = pd.concat(
        [st.session_state.df, new_row],
        ignore_index=True,
        copy=False
    )
    return schuljahr, False

def plural(n, s, p):
    return f"{n} {s if n == 1 else p}"

def dark_fig(w=9, h=4.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#1c1b22")
    ax.set_facecolor("#1c1b22")
    ax.tick_params(colors="#ccc8d8")
    for spine in ax.spines.values():
        spine.set_color("#2e2c38")
    return fig, ax

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* ── App background ── */
.stApp {
    background: linear-gradient(160deg, #0f0f11 0%, #13111a 60%, #0f0f11 100%);
    color: #e8e4dc;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #14131a;
    border-right: 1px solid #26242e;
    min-width: 280px !important;
    max-width: 280px !important;
    overflow: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1.2rem 1.2rem 1.2rem 1.2rem !important;
}

/* FIX 3: Disable sidebar resize handle */
div[data-testid="stSidebarResizeHandle"] {
    display: none !important;
}

/* ── Radio nav: dots + labels, no pointer cursor on container ── */
section[data-testid="stSidebar"] .stRadio > div { gap: 0.1rem !important; }
section[data-testid="stSidebar"] .stRadio { cursor: default !important; }
section[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
    color: #9a96a8 !important;
    padding: 0.42rem 0.7rem !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    transition: color 0.15s, background 0.15s !important;
    width: 100% !important;
    margin: 0 !important;
    user-select: none !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #e8e4dc !important;
    background: rgba(255,255,255,0.04) !important;
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    color: #c8f060 !important;
    background: rgba(200,240,96,0.07) !important;
}
/* Hide the "Menü" widget label text */
section[data-testid="stSidebar"] .stRadio div[data-testid="stWidgetLabel"] { display: none !important; }

/* Stats: push down with margin */
.sidebar-stats { margin-top: 1.5rem; font-size: 13px; line-height: 2; }

/* FIX 5: Speichern button – massive neon boss level */
section[data-testid="stMain"] .stButton > button {
    background: linear-gradient(135deg, #c8f060, #9cff00) !important;
    color: #0a0f00 !important;
    border: none !important;
    border-radius: 18px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 900 !important;
    font-size: 22px !important;
    padding: 1.4rem 2.4rem !important;
    width: 100% !important;
    letter-spacing: 0.1em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 0 35px rgba(200,240,96,0.6);
}

section[data-testid="stMain"] .stButton > button:hover {
    transform: scale(1.08);
    box-shadow:
        0 0 70px rgba(200,240,96,0.9),
        0 0 120px rgba(200,240,96,0.6);
}

section[data-testid="stMain"] .stButton > button:active {
    transform: scale(0.97);
}

/* ── Delete ✕ button: small, lime-green, no neon ── */
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] .stButton > button {
    background: transparent !important;
    border: 1px solid #3a5e2a !important;
    color: #80c860 !important;
    font-size: 11px !important;
    padding: 0.25rem 0.55rem !important;
    width: auto !important;
    box-shadow: none !important;
    transform: none !important;
    letter-spacing: 0 !important;
}
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #c8f060 !important;
    color: #c8f060 !important;
    background: rgba(200,240,96,0.06) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Metric cards ── */
.metric-card {
    background: rgba(28,27,34,0.7); border: 1px solid #282630;
    border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; transition: border-color 0.2s;
}
.metric-card:hover { border-color: #3a3844; }
.metric-card .label { font-size: 10px; color: #5e5a6b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
.metric-card .value {
    font-family: 'Syne', sans-serif; font-size: 2.1rem; font-weight: 800;
    background: linear-gradient(135deg, #c8f060, #80e0a0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1.1;
}
.metric-card .sub { font-size: 11px; color: #5e5a6b; margin-top: 0.3rem; }

/* ── Section header ── */
.section-header {
    font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800;
    color: #e8e4dc; border-bottom: 2px solid #c8f060;
    padding-bottom: 0.4rem; margin-bottom: 1.3rem; letter-spacing: -0.02em;
}

/* ── Note display ── */
.note-display {
    background: rgba(28,27,34,0.8); border: 1px solid #282630;
    border-radius: 10px; padding: 1.8rem 1.5rem; text-align: center;
}
.note-big { font-family: 'Syne', sans-serif; font-size: 3.5rem; font-weight: 800; line-height: 1; }
.note-green { background: linear-gradient(135deg, #80e080, #c8f060); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.note-yellow { background: linear-gradient(135deg, #f0d060, #e09840); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.note-red { background: linear-gradient(135deg, #f07878, #e04848); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

/* ── Messages ── */
.success-box { background: #1a2e1c; border: 1px solid #2e5e32; border-radius: 7px; padding: 0.5rem 1rem; color: #7ed87e; font-size: 12px; margin: 0.4rem 0; }
.warning-box { background: #221a0e; border: 1px solid #5e3e14; border-radius: 7px; padding: 0.65rem 1rem; color: #d4945a; font-size: 13px; margin: 0.5rem 0; }
.info-strip { background: rgba(26,28,38,0.8); border-left: 3px solid #4a6ea8; border-radius: 0 7px 7px 0; padding: 0.65rem 1rem; color: #9aacca; font-size: 12px; margin-bottom: 1rem; line-height: 1.6; }

/* ───────── CLEAN FOCUS SYSTEM ───────── */

/* FIX 1: Kill absolutely everything – single unified block, no conflicts */
*:focus,
*:focus-visible,
*:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

/* Inputs unified */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #1e1d2a !important;
    border: 1px solid #2e2c3e !important;
    border-radius: 8px !important;
    transition: border 0.15s ease !important;
}

/* Focus = subtle highlight, no glow, no outline */
.stTextInput input:focus,
.stNumberInput input:focus,
.stSelectbox div[data-baseweb="select"] > div:focus-within {
    border: 1px solid #c8f060 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Kill BaseWeb inner weird corners */
div[data-baseweb="select"] * {
    box-shadow: none !important;
    outline: none !important;
}

/* ── ALL inputs: color ── */
.stTextInput [data-baseweb="input"],
.stTextInput > div > div > input,
.stNumberInput [data-baseweb="input"],
.stNumberInput > div > div > input,
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox > div > div {
    background-color: #1e1d2a !important;
    border-color: #2e2c3e !important;
    color: #e8e4dc !important;
    outline: none !important;
}

.stNumberInput button {
    background-color: #1e1d2a !important;
    border-color: #2e2c3e !important;
    color: #9a96a8 !important;
}

/* ── Dropdown popup ── */
div[data-baseweb="popover"] {
    background-color: rgba(28, 26, 38, 0.97) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid #32303c !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}
div[data-baseweb="popover"] * { background-color: transparent !important; color: #e8e4dc !important; }
ul[role="listbox"] { background-color: transparent !important; padding: 0.3rem !important; }
ul[role="listbox"] li {
    background-color: transparent !important; color: #ccc8d8 !important;
    border-radius: 5px !important; padding: 0.4rem 0.8rem !important;
    font-size: 13px !important; transition: background 0.12s, color 0.12s !important;
}
ul[role="listbox"] li:hover { background-color: rgba(200,240,96,0.08) !important; color: #c8f060 !important; }
ul[role="listbox"] li[aria-selected="true"] { background-color: rgba(200,240,96,0.1) !important; color: #c8f060 !important; }

/* ── Hide "Press Enter" hint ── */
[data-testid="InputInstructions"] { display: none !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b6780 !important; font-family: 'DM Mono', monospace; font-size: 12px; transition: color 0.15s; }
.stTabs [data-baseweb="tab"]:hover { color: #c8f060 !important; }
.stTabs [aria-selected="true"] { color: #c8f060 !important; border-bottom-color: #c8f060 !important; }
.stTabs [data-baseweb="tab-list"] { border-bottom-color: #2a2830 !important; }

/* ── DataFrame Dark Styling ── */
div[data-testid="stDataFrame"] table {
    background-color: #1c1b22 !important;
    color: #e8e4dc !important;
}
div[data-testid="stDataFrame"] th {
    background-color: #23212c !important;
    color: #c8f060 !important;
    border-bottom: 1px solid #2e2c38 !important;
}
div[data-testid="stDataFrame"] td {
    background-color: #1c1b22 !important;
    border-bottom: 1px solid #2a2830 !important;
}
div[data-testid="stDataFrame"] tr:hover td {
    background-color: rgba(200,240,96,0.05) !important;
}

/* ── Slider ── */
.stSlider [role="slider"] { background-color: #c8f060 !important; border-color: #c8f060 !important; }

.stNumberInput input {
    background-color: #1e1d2a !important;
    color: #e8e4dc !important;
    border: 1px solid #2e2c3e !important;
}

/* FIX 6: Header dark – use background not background-color */
header[data-testid="stHeader"] {
    background: #0f0f11 !important;
}

hr { border-color: #2a2830; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───
with st.sidebar:
    # FIX 4: Logo not clipped – use white-space:normal and overflow:visible
    st.markdown("""
    <div style="
    font-family:'Syne',sans-serif;
    font-size:1.6rem;
    font-weight:800;
    background:linear-gradient(135deg,#c8f060,#80e0a0);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
    padding:0.6rem 0 1.4rem;
    letter-spacing:-0.02em;
    white-space:normal;
    overflow:visible;
    ">
    NotenTracker
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        " ",
        ["Dashboard", "Note hinzufügen", "Note löschen", "Analyse", "OCR Import"],
        label_visibility="hidden"
    )

    st.markdown("<div style='border-top:1px solid #26242e;margin-top:1.8rem;padding-top:1rem'></div>", unsafe_allow_html=True)

    d_side = st.session_state.df
    total = len(d_side)
    sj_count = d_side["Schuljahr"].nunique() if total > 0 else 0
    fach_count = d_side["Fach"].nunique() if total > 0 else 0
    st.markdown(f"""
    <div style="font-size:13px;line-height:2;color:#5a5768">
        <span style="color:#ccc8d8">{plural(total,'Note','Noten')}</span><br>
        <span style="color:#ccc8d8">{plural(sj_count,'Schuljahr','Schuljahre')}</span>
        <span style="color:#3a3748"> · </span>
        <span style="color:#ccc8d8">{plural(fach_count,'Fach','Fächer')}</span>
    </div>
    """, unsafe_allow_html=True)


# ─── DASHBOARD ───
if nav == "Dashboard":
    st.markdown('<div class="section-header">Dashboard</div>', unsafe_allow_html=True)
    d = st.session_state.df
    if d.empty:
        st.markdown('<div class="warning-box">Noch keine Noten vorhanden. Füge deine erste Note hinzu!</div>', unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg = round(d["Note"].mean(), 2)
            st.markdown(f'<div class="metric-card"><div class="label">Gesamtdurchschnitt</div><div class="value">{avg}</div><div class="sub">alle Fächer & Schuljahre</div></div>', unsafe_allow_html=True)
        with col2:
            best = d.loc[d["Note"].idxmin()]
            st.markdown(f'<div class="metric-card"><div class="label">Beste Note</div><div class="value">{best["Note"]:.2f}</div><div class="sub">{best["Fach"]} · {best["Zeitpunkt"]} · {best["Schuljahr"]}</div></div>', unsafe_allow_html=True)
        with col3:
            worst = d.loc[d["Note"].idxmax()]
            st.markdown(f'<div class="metric-card"><div class="label">Schlechteste Note</div><div class="value">{worst["Note"]:.2f}</div><div class="sub">{worst["Fach"]} · {worst["Zeitpunkt"]} · {worst["Schuljahr"]}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Alle Noten")
        display_df = d[["Schuljahr", "Fach", "Zeitpunkt", "Note"]].sort_values(["Schuljahr", "Fach", "Zeitpunkt"])
        st.dataframe(display_df, use_container_width=True, hide_index=True,
                     column_config={"Note": st.column_config.NumberColumn(format="%.2f")})

# ─── NOTE HINZUFÜGEN ───
elif nav == "Note hinzufügen":
    st.markdown('<div class="section-header">Note hinzufügen</div>', unsafe_allow_html=True)

    msg_placeholder = st.empty()

    # FIX 2: No threading, no sleep, no crash – show message directly, clear on next rerun
    if st.session_state.save_msg:
        msg_placeholder.markdown(
            f'<div class="success-box">{st.session_state.save_msg}</div>',
            unsafe_allow_html=True
        )
        st.session_state.save_msg = None

    col_form, col_note = st.columns([3, 2])
    with col_form:
        r1, r2 = st.columns(2)
        with r1:
            jahr = st.number_input("Jahr", min_value=2000, max_value=2100, value=2025, step=1)
        with r2:
            zeitpunkt = st.selectbox("Zeitpunkt", ["NSB1", "HJ", "NSB2", "Z"])
        fach = st.text_input("Fach", placeholder="z.B. Deutsch, Mathematik …").strip().capitalize()
        st.markdown("<div style='margin:0.4rem 0 0.1rem;font-size:13px;color:#7a7686'>Note</div>", unsafe_allow_html=True)
        note = st.slider("_s", min_value=1.0, max_value=6.0, value=3.0, step=0.01, format="%.2f", label_visibility="collapsed")
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        _, btn, _ = st.columns([1, 2, 1])
        with btn:
            if st.button("Speichern", key="save_btn"):
                if not fach:
                    st.markdown('<div class="warning-box">Bitte ein Fach eingeben.</div>', unsafe_allow_html=True)
                else:
                    save_note(int(jahr), fach, zeitpunkt, note)
                    st.session_state.save_msg = "✔ Gespeichert"
                    st.rerun()

    with col_note:
        klasse = note_klasse(note)
        label = "Sehr gut · Gut" if note <= 2 else ("Befriedigend · Ausreichend" if note <= 4 else "Mangelhaft · Ungenügend")
        st.markdown(f"""
        <div class="note-display" style="margin-top:2rem">
            <div style="font-size:10px;color:#5e5a6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem">Gewählte Note</div>
            <div class="note-big {klasse}">{note:.2f}</div>
            <div style="margin-top:0.8rem;font-size:11px;color:#5e5a6b">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── NOTE LÖSCHEN ───
elif nav == "Note löschen":
    st.markdown('<div class="section-header">Note löschen</div>', unsafe_allow_html=True)
    d = st.session_state.df
    if d.empty:
        st.markdown('<div class="warning-box">Keine Noten vorhanden.</div>', unsafe_allow_html=True)
    else:
        schuljahre = sorted(d["Schuljahr"].unique())
        fc1, fc2 = st.columns(2)
        with fc1:
            sj_sel = st.selectbox("Schuljahr", schuljahre)
        with fc2:
            df_sj = d[d["Schuljahr"] == sj_sel]
            faecher = sorted(df_sj["Fach"].unique())
            fach_sel = st.selectbox("Fach", faecher)

        df_fach = d[(d["Schuljahr"] == sj_sel) & (d["Fach"] == fach_sel)]
        for idx, row in df_fach.iterrows():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.markdown(f"<div style='line-height:2.2;color:#e8e4dc;font-size:13px'>{row['Zeitpunkt']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='line-height:2.2;color:#c8f060;font-family:Syne,sans-serif;font-weight:700;font-size:13px'>{row['Note']:.2f}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='line-height:2.2;color:#6b6780;font-size:13px'>{row['Schuljahr']}</div>", unsafe_allow_html=True)
            with c4:
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.df.drop(idx, inplace=True)
                    st.session_state.df.reset_index(drop=True, inplace=True)
                    st.rerun()

# ─── ANALYSE ───
elif nav == "Analyse":
    st.markdown('<div class="section-header">Analyse</div>', unsafe_allow_html=True)
    d = st.session_state.df
    if d.empty:
        st.markdown('<div class="warning-box">Keine Daten vorhanden.</div>', unsafe_allow_html=True)
    else:
        schuljahre = sorted(d["Schuljahr"].unique())
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Durchschnitt", "Stabilität", "Jahresverbesserung", "Notenentwicklung", "Schuljahre vergleichen"])

        with tab1:
            sj = st.selectbox("Schuljahr", schuljahre, key="t1")
            filtered = d[d["Schuljahr"] == sj]
            if filtered.empty:
                st.markdown(f'<div class="warning-box">Keine Daten für Schuljahr {sj}.</div>', unsafe_allow_html=True)
            else:
                result = filtered.groupby("Fach")["Note"].mean().round(2).reset_index()
                result.columns = ["Fach", "Durchschnitt"]
                st.dataframe(result, use_container_width=True, hide_index=True,
                             column_config={"Durchschnitt": st.column_config.NumberColumn(format="%.2f")})

        with tab2:
            st.markdown(
                '<div class="info-strip">Zeigt, wie stark deine Noten schwanken. Niedrig = konstant, hoch = starke Unterschiede.</div>',
                unsafe_allow_html=True
            )
            sj = st.selectbox("Schuljahr", schuljahre, key="t2")
            filtered = d[d["Schuljahr"] == sj]
            if filtered.empty:
                st.markdown(f'<div class="warning-box">Keine Daten für Schuljahr {sj}.</div>', unsafe_allow_html=True)
            else:
                rows = []
                for fach in filtered["Fach"].unique():
                    fdf = filtered[filtered["Fach"] == fach]
                    val = round(fdf["Note"].std(), 2) if len(fdf) >= 2 else "–"
                    rows.append({"Fach": fach, "Abweichung": val})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with tab3:
            sj = st.selectbox("Schuljahr", schuljahre, key="t3")
            filtered = d[d["Schuljahr"] == sj]
            if filtered.empty:
                st.markdown(f'<div class="warning-box">Keine Daten für Schuljahr {sj}.</div>', unsafe_allow_html=True)
            else:
                rows = []
                for fach in filtered["Fach"].unique():
                    fdf = filtered[filtered["Fach"] == fach].copy()
                    fdf["Zeit_num"] = fdf["Zeitpunkt"].map(zeit_map)
                    fdf = fdf.sort_values("Zeit_num")
                    if len(fdf) < 2:
                        rows.append({"Fach": fach, "Veränderung": "–", "Trend": "–"})
                        continue
                    diff = fdf.iloc[-1]["Note"] - fdf.iloc[0]["Note"]
                    trend = "Besser" if diff < 0 else ("Schlechter" if diff > 0 else "Gleich")
                    rows.append({"Fach": fach, "Veränderung": f"{round(diff, 2):+}", "Trend": trend})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with tab4:
            sj = st.selectbox("Schuljahr", schuljahre, key="t4")
            filtered = d[d["Schuljahr"] == sj]
            if filtered.empty:
                st.markdown(f'<div class="warning-box">Keine Daten für Schuljahr {sj}.</div>', unsafe_allow_html=True)
            else:
                zeit_reihenfolge = ["NSB1", "HJ", "NSB2", "Z"]
                x_mapping = {z: i for i, z in enumerate(zeit_reihenfolge)}
                colors = ["#c8f060", "#60d0f0", "#f060c8", "#f0c860", "#a060f0", "#f07060"]
                fig, ax = dark_fig(9, 5)
                for ci, fach in enumerate(filtered["Fach"].unique()):
                    fdf = filtered[filtered["Fach"] == fach]
                    vorhandene = [z for z in zeit_reihenfolge if z in fdf["Zeitpunkt"].values]
                    y = [fdf[fdf["Zeitpunkt"]==z]["Note"].iloc[0] for z in vorhandene]
                    x = [x_mapping[z] for z in vorhandene]
                    color = colors[ci % len(colors)]
                    if len(x) >= 2:
                        ax.plot(x, y, marker="o", linestyle="-", label=fach, color=color, linewidth=2.5, markersize=8)
                    else:
                        ax.scatter(x, y, label=fach, color=color, zorder=5, s=100)
                ax.set_xticks(list(x_mapping.values()))
                ax.set_xticklabels(list(x_mapping.keys()))
                ax.set_ylim(0.5, 6.5); ax.set_yticks([1,2,3,4,5,6])
                ax.set_xlabel("Zeitpunkt", color="#7a7686", labelpad=8)
                ax.set_ylabel("Note", color="#7a7686", labelpad=8)
                ax.set_title(f"Notenentwicklung – Schuljahr {sj}", color="#e8e4dc", fontsize=12, pad=12)
                ax.grid(True, color="#2e2c38", linewidth=0.7)
                ax.legend(facecolor="#1c1b22", edgecolor="#2e2c38", labelcolor="#ccc8d8")
                st.pyplot(fig)

        with tab5:
            if len(schuljahre) < 2:
                st.markdown('<div class="warning-box">Mindestens 2 Schuljahre erforderlich.</div>', unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                sj1 = c1.selectbox("Erstes Schuljahr", schuljahre, key="cmp1")
                sj2 = c2.selectbox("Zweites Schuljahr", schuljahre, index=min(1, len(schuljahre)-1), key="cmp2")
                if sj1 == sj2:
                    st.markdown('<div class="warning-box">Bitte zwei verschiedene Schuljahre auswählen.</div>', unsafe_allow_html=True)
                else:
                    df1 = d[d["Schuljahr"] == sj1]
                    df2 = d[d["Schuljahr"] == sj2]
                    avg1 = df1.groupby("Fach")["Note"].mean().round(2) if not df1.empty else pd.Series(dtype=float)
                    avg2 = df2.groupby("Fach")["Note"].mean().round(2) if not df2.empty else pd.Series(dtype=float)
                    all_faecher = sorted(set(avg1.index).union(set(avg2.index)))
                    rows = []
                    for fach in all_faecher:
                        w1 = f"{avg1[fach]:.2f}" if fach in avg1 else "/"
                        w2 = f"{avg2[fach]:.2f}" if fach in avg2 else "/"
                        rows.append({"Fach": fach, sj1: w1, sj2: w2})
                    g1 = f"{avg1.mean():.2f}" if not avg1.empty else "/"
                    g2 = f"{avg2.mean():.2f}" if not avg2.empty else "/"
                    rows.append({"Fach": "Ø Gesamt", sj1: g1, sj2: g2})
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                    avg_sj = d.groupby("Schuljahr")["Note"].mean().sort_index().round(2)
                    fig, ax = dark_fig(8, 4)
                    bar_colors = ["#c8f060" if sj in [sj1, sj2] else "#2e2c3e" for sj in avg_sj.index]
                    bars = ax.bar(avg_sj.index, avg_sj.values, color=bar_colors, width=0.5, edgecolor="#3a3848", linewidth=0.8)
                    for bar, val in zip(bars, avg_sj.values):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.07,
                                f"{val:.2f}", ha="center", va="bottom", color="#ccc8d8", fontsize=10, fontfamily="monospace")
                    ax.set_ylim(0.5, 7.2); ax.set_yticks([1,2,3,4,5,6])
                    ax.set_xlabel("Schuljahr", color="#7a7686", labelpad=8)
                    ax.set_ylabel("Note", color="#7a7686", labelpad=8)
                    ax.set_title("Gesamtdurchschnitt pro Schuljahr", color="#e8e4dc", fontsize=12, pad=12)
                    ax.grid(axis="y", color="#2e2c38", linewidth=0.7)
                    st.pyplot(fig)

# ─── OCR IMPORT ───
elif nav == "OCR Import":
    st.markdown('<div class="section-header">OCR Import</div>', unsafe_allow_html=True)
    st.markdown("<div style='color:#7a7686;font-size:13px;margin-bottom:1rem'>Lade ein Bild hoch, um Noten per OCR zu erkennen.</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Bild hochladen", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    if uploaded:
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        st.image(tmp_path, caption="Hochgeladenes Bild", use_column_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### EasyOCR")
            if st.button("EasyOCR starten", key="easy_ocr"):
                with st.spinner("Wird verarbeitet …"):
                    try:
                        from easyocr import Reader
                        reader = Reader(['de'], gpu=False)
                        results = reader.readtext(tmp_path, detail=0)
                        st.text_area("Ergebnis", "\n".join(results), height=280)
                    except Exception as e:
                        st.error(f"EasyOCR Fehler: {e}")
        with col2:
            st.markdown("#### PaddleOCR")
            if st.button("PaddleOCR starten", key="paddle_ocr"):
                with st.spinner("Wird verarbeitet …"):
                    try:
                        from paddleocr import PaddleOCR
                        ocr = PaddleOCR(lang='german', use_angle_cls=False, use_gpu=False, show_log=False)
                        result = ocr.ocr(tmp_path, cls=False)
                        lines = [text for line in result for _, (text, _) in line]
                        st.text_area("Ergebnis", "\n".join(lines), height=280)
                    except Exception as e:
                        st.error(f"PaddleOCR Fehler: {e}")
        os.unlink(tmp_path)
    else:
        st.markdown('<div class="warning-box">Bitte ein Bild hochladen um OCR zu starten.</div>', unsafe_allow_html=True)