import streamlit as st
import utils.auth as auth


def render():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:1.8rem;">
                <span style="
                    background:#6DCFF6;color:#1A3A6B;font-size:0.75rem;
                    font-weight:800;letter-spacing:0.18em;
                    padding:0.25rem 0.7rem;border-radius:4px;
                ">KUMON</span>
                <h2 style="color:#1A3A6B;font-size:1.5rem;font-weight:700;margin:0.6rem 0 0;">
                    Admin Login
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if auth.is_locked_out("admin"):
            secs = auth.lockout_seconds_remaining("admin")
            st.error(f"Too many failed attempts. Please wait {secs // 60}m {secs % 60}s.")
            if st.button("← Back to Home", type="secondary", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            return

        st.markdown(
            """
            <div style="background:white;border:1px solid #ADE3F6;border-radius:12px;
                        padding:2rem;box-shadow:0 2px 12px rgba(0,48,135,0.08);">
            """,
            unsafe_allow_html=True,
        )

        password = st.text_input("Admin password", type="password", placeholder="Enter admin password")

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
                remaining = max(0, 5 - st.session_state.get("_failed_admin", 0))
                st.error(f"Incorrect password. {remaining} attempt(s) left before lockout.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", type="tertiary", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
