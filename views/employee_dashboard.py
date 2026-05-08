import streamlit as st
import pandas as pd
from datetime import datetime, date
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
        st.markdown(
            f"""
            <div style="margin-bottom:0.5rem;">
                <span style="
                    background:#003087;color:white;font-size:0.75rem;
                    font-weight:800;letter-spacing:0.18em;
                    padding:0.25rem 0.7rem;border-radius:4px;
                ">KUMON</span>
                <span style="color:#003087;font-size:1.3rem;font-weight:700;margin-left:0.75rem;">
                    My Hours — {emp_name}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("← Back", type="secondary", use_container_width=True):
            st.session_state.employee_id = None
            st.session_state.employee_name = None
            st.session_state.page = "employee_login"
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #C8D4EF;margin:0.8rem 0 1.2rem;'>",
                unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    today = date.today()
    col_a, col_b = st.columns(2)
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
        st.info("No entries found for this period.")
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

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div style="background:#EEF3FF;border:1px solid #C8D4EF;border-radius:8px;
                    padding:0.8rem 1.2rem;margin-top:0.5rem;display:inline-block;">
            <span style="color:#003087;font-weight:700;">Total: {_fmt_duration(total_secs)}</span>
            <span style="color:#667;font-size:0.88rem;margin-left:0.75rem;">
                ({len([r for r in rows if r['Clock Out'] != 'Still clocked in'])} shifts)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
