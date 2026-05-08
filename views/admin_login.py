import streamlit as st
import utils.auth as auth


def render():
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("### Admin Login")

        if auth.is_locked_out("admin"):
            secs = auth.lockout_seconds_remaining("admin")
            st.error(f"Too many failed attempts. Please wait {secs // 60}m {secs % 60}s.")
            if st.button("← Back"):
                st.session_state.page = "home"
                st.rerun()
            return

        password = st.text_input("Admin password", type="password")

        if st.button("Log In", type="primary", use_container_width=True):
            if not password:
                st.error("Please enter the admin password.")
            elif auth.check_admin_login(password):
                auth.reset_failed_attempts("admin")
                st.session_state.admin_logged_in = True
                st.session_state.page = "admin_area"
                st.rerun()
            else:
                auth.record_failed_attempt("admin")
                remaining = 5 - st.session_state.get("_failed_admin", 0)
                st.error(f"Incorrect password. {remaining} attempt(s) remaining before lockout.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
