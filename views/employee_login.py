import streamlit as st
from datetime import datetime
import pytz
import utils.auth as auth
import utils.database as db


def _header():
    st.markdown(
        """
        <div style="margin-bottom:1.2rem;">
            <span style="
                background:#6DCFF6;color:#1A3A6B;font-size:0.75rem;
                font-weight:800;letter-spacing:0.18em;
                padding:0.25rem 0.7rem;border-radius:4px;
            ">KUMON</span>
            <span style="color:#1A3A6B;font-size:1.3rem;font-weight:700;margin-left:0.75rem;">
                Employee Clock-In
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render():
    tz = db.get_tz()

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        _header()

        # ── Lockout check ──────────────────────────────────────────────────
        if auth.is_locked_out("employee"):
            secs = auth.lockout_seconds_remaining("employee")
            st.error(f"Too many failed attempts. Please wait {secs // 60}m {secs % 60}s.")
            if st.button("← Back to Home", type="secondary", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            return

        # ── Success state after clock in/out ──────────────────────────────
        if st.session_state.get("emp_action_done"):
            action = st.session_state.emp_action_type
            ts: datetime = st.session_state.emp_action_time
            name = st.session_state.emp_action_name
            ts_local = ts.astimezone(tz).strftime("%I:%M %p")

            if action == "clock_in":
                st.markdown(
                    f"""
                    <div style="background:#E8F7FD;border:1px solid #ADE3F6;border-radius:10px;
                                padding:1.5rem;text-align:center;margin-bottom:1rem;">
                        <div style="font-size:2rem;margin-bottom:0.5rem;">✓</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#1A3A6B;">
                            Clocked in at {ts_local}
                        </div>
                        <div style="color:#555;margin-top:0.3rem;">Have a great shift, {name}!</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background:#E8F7FD;border:1px solid #ADE3F6;border-radius:10px;
                                padding:1.5rem;text-align:center;margin-bottom:1rem;">
                        <div style="font-size:2rem;margin-bottom:0.5rem;">👋</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#1A3A6B;">
                            Clocked out at {ts_local}
                        </div>
                        <div style="color:#555;margin-top:0.3rem;">See you next time, {name}!</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("View Hours", use_container_width=True, type="primary"):
                    st.session_state.page = "employee_dashboard"
                    st.session_state.emp_action_done = False
                    st.rerun()
            with c2:
                if st.button("Done", use_container_width=True, type="secondary"):
                    st.session_state.emp_action_done = False
                    st.session_state.employee_id = None
                    st.session_state.employee_name = None
                    st.session_state.page = "home"
                    st.rerun()
            return

        # ── Main form ──────────────────────────────────────────────────────
        employees = db.get_active_employees()
        if not employees:
            st.warning("No employees configured yet. Ask your admin to add employees.")
            if st.button("← Back", type="secondary", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            return

        names = [e["name"] for e in employees]

        if "emp_selected_name" not in st.session_state:
            st.session_state.emp_selected_name = names[0]

        name = st.selectbox(
            "Your name",
            names,
            index=names.index(st.session_state.emp_selected_name)
            if st.session_state.emp_selected_name in names else 0,
        )
        if name != st.session_state.emp_selected_name:
            st.session_state.emp_selected_name = name

        emp_record = next((e for e in employees if e["name"] == name), None)
        currently_in = db.is_clocked_in(emp_record["id"]) if emp_record else False

        if currently_in:
            st.markdown(
                "<div style='color:#1A8A3A;font-size:0.88rem;font-weight:600;margin:-0.2rem 0 0.5rem;'>"
                "● Currently clocked in</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='color:#888;font-size:0.88rem;font-weight:600;margin:-0.2rem 0 0.5rem;'>"
                "○ Currently clocked out</div>",
                unsafe_allow_html=True,
            )

        password = st.text_input("Password", type="password", placeholder="Enter your password")

        st.markdown(
            "<hr style='border:none;border-top:1px solid #ADE3F6;margin:0.8rem 0;'>",
            unsafe_allow_html=True,
        )

        btn_label = "Clock Out" if currently_in else "Clock In"
        c1, c2 = st.columns(2)
        with c1:
            clock_clicked = st.button(btn_label, type="primary", use_container_width=True)
        with c2:
            hours_clicked = st.button("View Hours", type="secondary", use_container_width=True)

        if clock_clicked or hours_clicked:
            if not password:
                st.error("Please enter your password.")
            else:
                employee = auth.check_employee_login(name, password)
                if not employee:
                    auth.record_failed_attempt("employee")
                    remaining = max(0, 5 - st.session_state.get("_failed_employee", 0))
                    st.error(f"Incorrect password. {remaining} attempt(s) left before lockout.")
                else:
                    auth.reset_failed_attempts("employee")
                    st.session_state.employee_id = employee["id"]
                    st.session_state.employee_name = employee["name"]

                    if hours_clicked:
                        st.session_state.emp_action_done = False
                        st.session_state.page = "employee_dashboard"
                        st.rerun()
                    elif clock_clicked:
                        now = datetime.now(pytz.utc)
                        if currently_in:
                            db.clock_out(employee["id"])
                            st.session_state.emp_action_type = "clock_out"
                        else:
                            db.clock_in(employee["id"])
                            st.session_state.emp_action_type = "clock_in"
                        st.session_state.emp_action_done = True
                        st.session_state.emp_action_time = now
                        st.session_state.emp_action_name = employee["name"]
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", type="tertiary", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
