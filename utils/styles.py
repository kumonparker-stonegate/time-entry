import streamlit as st

# Kumon sky blue + dark navy companion
PRIMARY   = "#6DCFF6"
DARK      = "#1A3A6B"
LIGHT     = "#E8F7FD"
BORDER    = "#ADE3F6"
BG        = "#F7FBFF"

CSS = """
<style>
/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stApp { background-color: #F7FBFF; }
.block-container { padding-top: 2.5rem !important; max-width: 860px; }

/* ── Force light inputs (overrides dark mode) ─────────────────────────────── */
div.stTextInput > div > div > input {
    background-color: white !important;
    color: #1A3A6B !important;
    border: 1.5px solid #ADE3F6 !important;
    border-radius: 8px !important;
}
div.stTextInput > div > div > input:focus {
    border-color: #6DCFF6 !important;
    box-shadow: 0 0 0 2px rgba(109,207,246,0.25) !important;
}
div.stSelectbox > div > div {
    background-color: white !important;
    color: #1A3A6B !important;
    border: 1.5px solid #ADE3F6 !important;
    border-radius: 8px !important;
}
/* selectbox text */
div.stSelectbox > div > div > div {
    color: #1A3A6B !important;
}

/* ── Global text color (overrides dark mode) ─────────────────────────────── */
.stApp, .stApp p, .stApp li, .stApp span,
.stMarkdown, .stMarkdown p { color: #1A3A6B; }

/* ── Labels ───────────────────────────────────────────────────────────────── */
div.stTextInput > label, div.stSelectbox > label,
div.stDateInput > label, div.stMultiSelect > label {
    font-weight: 500 !important;
    color: #1A3A6B !important;
}

/* ── Primary buttons ──────────────────────────────────────────────────────── */
div.stButton > button[kind="primary"] {
    background-color: #6DCFF6 !important;
    color: #1A3A6B !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(109,207,246,0.4) !important;
    transition: all 0.18s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #4BBFE8 !important;
    box-shadow: 0 4px 12px rgba(109,207,246,0.5) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* ── Secondary buttons ────────────────────────────────────────────────────── */
div.stButton > button[kind="secondary"] {
    background-color: white !important;
    color: #1A3A6B !important;
    border: 2px solid #6DCFF6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.18s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    background-color: #E8F7FD !important;
}

/* ── Tertiary / plain buttons ─────────────────────────────────────────────── */
div.stButton > button[kind="tertiary"] {
    color: #1A3A6B !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.5rem !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #ADE3F6; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0 !important;
    font-weight: 600 !important;
    color: #777 !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: #1A3A6B !important;
    border-bottom: 3px solid #6DCFF6 !important;
    background-color: #E8F7FD !important;
}

/* ── Alerts ───────────────────────────────────────────────────────────────── */
div.stSuccess { border-left: 4px solid #6DCFF6 !important; }
div.stInfo    { border-left: 4px solid #6DCFF6 !important; }

/* ── Dataframe header ─────────────────────────────────────────────────────── */
.stDataFrame thead tr th {
    background-color: #1A3A6B !important;
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
