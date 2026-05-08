import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
import utils.database as db
import utils.auth as auth
from utils.pdf_gen import generate_report_pdf


def _fmt_duration(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"


def _parse_entries_to_df(entries: list, tz: pytz.BaseTzInfo) -> pd.DataFrame:
    rows = []
    for e in entries:
        ci = datetime.fromisoformat(e["clock_in"])
        co = datetime.fromisoformat(e["clock_out"]) if e["clock_out"] else None
        if ci.tzinfo is None:
            ci = pytz.utc.localize(ci)
        if co and co.tzinfo is None:
            co = pytz.utc.localize(co)
        ci_local = ci.astimezone(tz)
        co_local = co.astimezone(tz) if co else None
        secs = (co - ci).total_seconds() if co else None
        rows.append({
            "_id": e["id"],
            "Employee": e["employees"]["name"] if e.get("employees") else "",
            "Clock In": ci_local.replace(tzinfo=None),
            "Clock Out": co_local.replace(tzinfo=None) if co_local else None,
            "Duration": _fmt_duration(secs) if secs else "Open",
        })
    return pd.DataFrame(rows)


# ── Tab: Dashboard ────────────────────────────────────────────────────────────

def _tab_dashboard():
    st.markdown("#### Currently Clocked In")

    clocked_in = db.get_currently_clocked_in()
    tz = db.get_tz()

    if not clocked_in:
        st.info("No employees are currently clocked in.")
    else:
        for entry in clocked_in:
            ci = entry["clock_in"]
            if ci.tzinfo is None:
                ci = pytz.utc.localize(ci)
            ci_local = ci.astimezone(tz)
            elapsed = datetime.now(pytz.utc) - ci
            col1, col2, col3 = st.columns([3, 2, 1.5])
            with col1:
                st.write(f"**{entry['employee_name']}**")
            with col2:
                st.write(f"Since {ci_local.strftime('%I:%M %p')}  ({_fmt_duration(elapsed.total_seconds())} ago)")
            with col3:
                if st.button("Clock Out", key=f"co_{entry['entry_id']}"):
                    db.force_clock_out(entry["entry_id"])
                    st.success(f"Clocked out {entry['employee_name']}.")
                    st.rerun()

    st.markdown("---")
    st.markdown(f"**{len(clocked_in)} employee(s) currently clocked in.**")

    if st.button("Refresh", use_container_width=False):
        st.rerun()


# ── Tab: Hours ────────────────────────────────────────────────────────────────

def _tab_hours():
    st.markdown("#### View & Edit Hours")
    tz = db.get_tz()

    employees = db.get_active_employees()
    emp_options = ["All Employees"] + [e["name"] for e in employees]

    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        selected_emp = st.selectbox("Employee", emp_options, key="ah_emp")
    today = date.today()
    with col2:
        start = st.date_input("From", value=today.replace(day=1), key="ah_start")
    with col3:
        end = st.date_input("To", value=today, key="ah_end")

    if start > end:
        st.warning("Start date must be before end date.")
        return

    emp_id = None
    if selected_emp != "All Employees":
        match = next((e for e in employees if e["name"] == selected_emp), None)
        emp_id = match["id"] if match else None

    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=pytz.utc)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=pytz.utc)

    entries = db.get_time_entries(employee_id=emp_id, start_date=start_dt, end_date=end_dt)

    if not entries:
        st.info("No entries found for the selected filters.")
        return

    df = _parse_entries_to_df(entries, tz)
    original_ids = df["_id"].tolist()

    st.markdown(f"**{len(df)} entries found.**")
    st.markdown(
        "_Editing: click a Clock In or Clock Out cell to change the time. "
        "Select a row checkbox and press delete to remove an entry. Click **Save Changes** when done._"
    )

    edited = st.data_editor(
        df.drop(columns=["_id"]),
        column_config={
            "Employee": st.column_config.TextColumn("Employee", disabled=True),
            "Clock In": st.column_config.DatetimeColumn("Clock In", format="MM/DD/YYYY hh:mm a"),
            "Clock Out": st.column_config.DatetimeColumn("Clock Out", format="MM/DD/YYYY hh:mm a"),
            "Duration": st.column_config.TextColumn("Duration", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="hours_editor",
    )

    if st.button("Save Changes", type="primary"):
        original_df = df.drop(columns=["_id"])
        # Deleted rows: rows in original that aren't in edited (by index)
        deleted_indices = set(range(len(original_df))) - set(edited.index)
        for i in sorted(deleted_indices):
            if i < len(original_ids):
                db.delete_time_entry(original_ids[i])

        # Changed rows
        for i in edited.index:
            if i >= len(original_ids):
                continue
            orig_row = original_df.iloc[i]
            edit_row = edited.iloc[i]
            ci_changed = str(orig_row["Clock In"]) != str(edit_row["Clock In"])
            co_changed = str(orig_row["Clock Out"]) != str(edit_row["Clock Out"])
            if ci_changed or co_changed:
                ci_val = edit_row["Clock In"]
                co_val = edit_row["Clock Out"]
                if pd.isna(ci_val):
                    st.error(f"Row {i + 1}: Clock In cannot be empty.")
                    continue
                ci_dt = pd.Timestamp(ci_val).tz_localize(tz).tz_convert(pytz.utc)
                co_dt = pd.Timestamp(co_val).tz_localize(tz).tz_convert(pytz.utc) if not pd.isna(co_val) else None
                db.update_time_entry(original_ids[i], ci_dt.to_pydatetime(), co_dt.to_pydatetime() if co_dt else None)

        st.success("Changes saved.")
        st.rerun()


# ── Tab: Reports ──────────────────────────────────────────────────────────────

def _tab_reports():
    st.markdown("#### Download Reports")
    tz = db.get_tz()

    employees = db.get_active_employees()
    emp_names = [e["name"] for e in employees]
    selected_emps = st.multiselect("Filter by employee (leave blank for all)", emp_names, key="rep_emp")

    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("From", value=today.replace(day=1), key="rep_start")
    with col2:
        end = st.date_input("To", value=today, key="rep_end")

    if start > end:
        st.warning("Start date must be before end date.")
        return

    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=pytz.utc)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=pytz.utc)

    st.markdown("---")
    col_csv, col_pdf = st.columns(2)

    with col_csv:
        if st.button("Generate CSV", use_container_width=True):
            all_entries = []
            target_emps = [e for e in employees if not selected_emps or e["name"] in selected_emps]
            for emp in target_emps:
                entries = db.get_time_entries(employee_id=emp["id"], start_date=start_dt, end_date=end_dt)
                all_entries.extend(entries)

            rows = []
            for e in all_entries:
                ci = datetime.fromisoformat(e["clock_in"])
                co = datetime.fromisoformat(e["clock_out"]) if e["clock_out"] else None
                if ci.tzinfo is None:
                    ci = pytz.utc.localize(ci)
                if co and co.tzinfo is None:
                    co = pytz.utc.localize(co)
                ci_local = ci.astimezone(tz)
                co_local = co.astimezone(tz) if co else None
                secs = (co - ci).total_seconds() if co else None
                rows.append({
                    "Employee": e["employees"]["name"] if e.get("employees") else "",
                    "Date": ci_local.strftime("%Y-%m-%d"),
                    "Clock In": ci_local.strftime("%H:%M"),
                    "Clock Out": co_local.strftime("%H:%M") if co_local else "",
                    "Hours": round(secs / 3600, 2) if secs else "",
                })

            if not rows:
                st.warning("No completed entries found for the selected period.")
            else:
                df = pd.DataFrame(rows)
                csv_bytes = df.to_csv(index=False).encode()
                fname = f"kumon_hours_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
                st.download_button("Download CSV", csv_bytes, file_name=fname, mime="text/csv", use_container_width=True)

    with col_pdf:
        if st.button("Generate PDF", use_container_width=True):
            all_entries = []
            target_emps = [e for e in employees if not selected_emps or e["name"] in selected_emps]
            for emp in target_emps:
                raw = db.get_time_entries(employee_id=emp["id"], start_date=start_dt, end_date=end_dt)
                for r in raw:
                    r["employee_name"] = emp["name"]
                all_entries.extend(raw)

            if not all_entries:
                st.warning("No completed entries found for the selected period.")
            else:
                tz_str = st.secrets.get("TIMEZONE", "America/New_York")
                pdf_bytes = generate_report_pdf(all_entries, start, end, tz_str)
                fname = f"kumon_report_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pdf"
                st.download_button("Download PDF", pdf_bytes, file_name=fname, mime="application/pdf", use_container_width=True)


# ── Tab: Employees ────────────────────────────────────────────────────────────

def _tab_employees():
    st.markdown("#### Manage Employees")

    employees = db.get_all_employees()

    for emp in employees:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            status = "Active" if emp["is_active"] else "Inactive"
            st.write(f"**{emp['name']}**  —  {status}")
        with col2:
            label = "Deactivate" if emp["is_active"] else "Reactivate"
            if st.button(label, key=f"toggle_{emp['id']}"):
                db.set_employee_active(emp["id"], not emp["is_active"])
                st.rerun()
        with col3:
            with st.popover("Reset Password"):
                new_pw = st.text_input("New password", type="password", key=f"pw_{emp['id']}")
                if st.button("Save Password", key=f"savepw_{emp['id']}"):
                    if len(new_pw) < 4:
                        st.error("Password must be at least 4 characters.")
                    else:
                        db.update_employee_password(emp["id"], auth.hash_password(new_pw))
                        st.success("Password updated.")

    st.markdown("---")
    st.markdown("#### Add New Employee")

    with st.form("add_employee_form", clear_on_submit=True):
        new_name = st.text_input("Full name")
        new_pw = st.text_input("Temporary password", type="password")
        submitted = st.form_submit_button("Add Employee", type="primary")

    if submitted:
        if not new_name.strip():
            st.error("Name cannot be empty.")
        elif len(new_pw) < 4:
            st.error("Password must be at least 4 characters.")
        elif any(e["name"].lower() == new_name.strip().lower() for e in employees):
            st.error(f'An employee named "{new_name.strip()}" already exists.')
        else:
            db.add_employee(new_name.strip(), auth.hash_password(new_pw))
            st.success(f"Added {new_name.strip()}. They can log in with their name and the password you set.")
            st.rerun()


# ── Main render ───────────────────────────────────────────────────────────────

def render():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            """
            <div style="margin-bottom:0.3rem;">
                <span style="
                    background:#6DCFF6;color:#1A3A6B;font-size:0.75rem;
                    font-weight:800;letter-spacing:0.18em;
                    padding:0.25rem 0.7rem;border-radius:4px;
                ">KUMON</span>
                <span style="color:#1A3A6B;font-size:1.3rem;font-weight:700;margin-left:0.75rem;">
                    Admin Panel
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Log Out", type="secondary", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.page = "home"
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #ADE3F6;margin:0.5rem 0 1rem;'>",
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["  Dashboard  ", "  Hours  ", "  Reports  ", "  Employees  "])

    with tab1:
        _tab_dashboard()
    with tab2:
        _tab_hours()
    with tab3:
        _tab_reports()
    with tab4:
        _tab_employees()
