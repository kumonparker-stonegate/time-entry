import streamlit as st
import utils.auth as auth
import utils.database as db


def render():
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("### Employee Login")

        if auth.is_locked_out("employee"):
            secs = auth.lockout_seconds_remaining("employee")
            st.error(f"Too many failed attempts. Please wait {secs // 60}m {secs % 60}s before trying again.")
            if st.button("← Back"):
                st.session_state.page = "home"
                st.rerun()
            return

        employees = db.get_active_employees()
        if not employees:
            st.warning("No employees found. Ask your admin to add employees first.")
            if st.button("← Back"):
                st.session_state.page = "home"
                st.rerun()
            return

        names = [e["name"] for e in employees]
        name = st.selectbox("Your name", names)
        password = st.text_input("Password", type="password")

        if st.button("Log In", type="primary", use_container_width=True):
            if not password:
                st.error("Please enter your password.")
            else:
                employee = auth.check_employee_login(name, password)
                if employee:
                    auth.reset_failed_attempts("employee")
                    st.session_state.employee_id = employee["id"]
                    st.session_state.employee_name = employee["name"]
                    st.session_state.page = "employee_dashboard"
                    st.rerun()
                else:
                    auth.record_failed_attempt("employee")
                    remaining = 5 - st.session_state.get("_failed_employee", 0)
                    st.error(f"Incorrect password. {remaining} attempt(s) remaining before lockout.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
