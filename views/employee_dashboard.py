import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
import utils.database as db


def _fmt_duration(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"


def render():
    tz = db.get_tz()
    emp_id = st.session_state.employee_id
    emp_name = st.session_state.employee_name

    # ── Header ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"### Welcome, {emp_name}")
    with col2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.employee_id = None
            st.session_state.employee_name = None
            st.session_state.page = "home"
            st.rerun()

    st.markdown("---")

    # ── Clock in/out status ───────────────────────────────────────────────────
    clocked_in = db.is_clocked_in(emp_id)
    open_entry = db.get_open_entry(emp_id) if clocked_in else None

    if clocked_in and open_entry:
        ci_dt = datetime.fromisoformat(open_entry["clock_in"])
        if ci_dt.tzinfo is None:
            ci_dt = pytz.utc.localize(ci_dt)
        ci_local = ci_dt.astimezone(tz)
        elapsed = datetime.now(pytz.utc) - ci_dt
        elapsed_str = _fmt_duration(elapsed.total_seconds())

        st.success(f"You are **clocked in** since {ci_local.strftime('%I:%M %p')} — {elapsed_str} elapsed")
        if st.button("Clock Out", type="primary", use_container_width=True):
            db.clock_out(emp_id)
            st.success("You have clocked out. See you next time!")
            st.rerun()
    else:
        st.info("You are **clocked out**.")
        if st.button("Clock In", type="primary", use_container_width=True):
            db.clock_in(emp_id)
            st.success("You are now clocked in!")
            st.rerun()

    st.markdown("---")

    # ── Hours history ─────────────────────────────────────────────────────────
    st.markdown("#### My Hours")

    col_a, col_b = st.columns(2)
    today = date.today()
    with col_a:
        start = st.date_input("From", value=today.replace(day=1))
    with col_b:
        end = st.date_input("To", value=today)

    if start > end:
        st.warning("Start date must be before end date.")
        return

    start_dt = datetime.combine(start, datetime.min.time()).replace(tzinfo=pytz.utc)
    end_dt = datetime.combine(end, datetime.min.time()).replace(tzinfo=pytz.utc)

    entries = db.get_time_entries(employee_id=emp_id, start_date=start_dt, end_date=end_dt)

    if not entries:
        st.write("No entries found for this period.")
        return

    rows = []
    total_secs = 0.0
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
        if secs:
            total_secs += secs
        rows.append({
            "Date": ci_local.strftime("%a, %b %d"),
            "Clock In": ci_local.strftime("%I:%M %p"),
            "Clock Out": co_local.strftime("%I:%M %p") if co_local else "Still clocked in",
            "Duration": _fmt_duration(secs) if secs else "—",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown(f"**Total hours: {_fmt_duration(total_secs)}**")
