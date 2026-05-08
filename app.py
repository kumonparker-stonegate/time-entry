import streamlit as st

st.set_page_config(
    page_title="Kumon Time Entry",
    page_icon="🕐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide sidebar toggle and default Streamlit menu for a cleaner look
st.markdown(
    """
    <style>
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none; }
    .block-container { padding-top: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state defaults ─────────────────────────────────────────────────────
for key, default in [
    ("page", "home"),
    ("employee_id", None),
    ("employee_name", None),
    ("admin_logged_in", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Router ─────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from views.home import render
    render()

elif page == "employee_login":
    from views.employee_login import render
    render()

elif page == "employee_dashboard":
    if not st.session_state.employee_id:
        st.session_state.page = "employee_login"
        st.rerun()
    else:
        from views.employee_dashboard import render
        render()

elif page == "admin_login":
    from views.admin_login import render
    render()

elif page == "admin_area":
    if not st.session_state.admin_logged_in:
        st.session_state.page = "admin_login"
        st.rerun()
    else:
        from views.admin_area import render
        render()

else:
    st.session_state.page = "home"
    st.rerun()
