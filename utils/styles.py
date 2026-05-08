import streamlit as st

KUMON_BLUE = "#003087"
KUMON_BLUE_HOVER = "#0047BD"
KUMON_LIGHT = "#EEF3FF"
KUMON_BORDER = "#C8D4EF"

CSS = """
<style>
/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stApp { background-color: #F7F9FF; }
.block-container { padding-top: 2.5rem !important; }

/* ── Primary buttons ──────────────────────────────────────────────────────── */
div.stButton > button[kind="primary"] {
    background-color: #003087 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.5rem !important;
    box-shadow: 0 2px 6px rgba(0,48,135,0.25) !important;
    transition: all 0.18s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #0047BD !important;
    box-shadow: 0 4px 10px rgba(0,48,135,0.35) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* ── Secondary buttons ────────────────────────────────────────────────────── */
div.stButton > button[kind="secondary"] {
    background-color: white !important;
    color: #003087 !important;
    border: 2px solid #003087 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.18s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    background-color: #EEF3FF !important;
}

/* ── Tertiary / plain buttons ─────────────────────────────────────────────── */
div.stButton > button[kind="tertiary"] {
    color: #003087 !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.5rem !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #C8D4EF; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0 !important;
    font-weight: 600 !important;
    color: #555 !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: #003087 !important;
    border-bottom: 3px solid #003087 !important;
    background-color: #EEF3FF !important;
}

/* ── Inputs ───────────────────────────────────────────────────────────────── */
div.stTextInput > label, div.stSelectbox > label,
div.stDateInput > label, div.stMultiSelect > label { font-weight: 500 !important; }

div.stTextInput > div > div > input,
div.stSelectbox > div > div { border-radius: 8px !important; }

/* ── Alerts ───────────────────────────────────────────────────────────────── */
div.stSuccess { border-left: 4px solid #003087 !important; }
div.stInfo    { border-left: 4px solid #0066CC !important; }

/* ── Dataframe ────────────────────────────────────────────────────────────── */
.stDataFrame thead tr th {
    background-color: #003087 !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────────────── */
#MainMenu, header, footer { visibility: hidden; }
[data-testid="collapsedControl"] { display: none; }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
