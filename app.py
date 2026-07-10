import streamlit as st

st.set_page_config(
    page_title="Kumon Time Entry",
    page_icon="🕐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from utils.styles import inject
inject()

# ── Session state defaults ─────────────────────────────────────────────────────
for key, default in [
    ("page", "home"),
    ("employee_id", None),
    ("employee_name", None),
    ("admin_logged_in", False),
    ("emp_action_done", False),
    ("emp_action_type", None),
    ("emp_action_time", None),
    ("emp_action_name", None),
    ("emp_selected_name", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Router ─────────────────────────────────────────────────────────────────────
page = st.session_state.page

def _db_error():
    st.error("Unable to connect to the database. Please refresh the page.")
    st.caption("If this keeps happening, the database may be temporarily unavailable.")
    if st.button("Refresh"):
        st.rerun()

try:
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

except Exception as e:
    if type(e).__name__ in ("ConnectError", "APIError"):
        _db_error()
    else:
        raise
