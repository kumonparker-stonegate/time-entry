import bcrypt
import streamlit as st
from datetime import datetime, timedelta
import utils.database as db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def check_employee_login(name: str, password: str) -> dict | None:
    employee = db.get_employee_by_name(name)
    if employee and verify_password(password, employee["password_hash"]):
        return employee
    return None


def check_admin_login(password: str) -> bool:
    return verify_password(password, st.secrets["ADMIN_PASSWORD_HASH"])


# ---------------------------------------------------------------------------
# Lockout helpers  (per-session, keyed by a string like "employee" or "admin")
# ---------------------------------------------------------------------------

def _count_key(key: str) -> str:
    return f"_failed_{key}"


def _lockout_key(key: str) -> str:
    return f"_lockout_{key}"


def is_locked_out(key: str) -> bool:
    lk = _lockout_key(key)
    if lk in st.session_state:
        if datetime.now() < st.session_state[lk]:
            return True
        del st.session_state[lk]
        st.session_state[_count_key(key)] = 0
    return False


def lockout_seconds_remaining(key: str) -> int:
    lk = _lockout_key(key)
    if lk in st.session_state:
        return max(0, int((st.session_state[lk] - datetime.now()).total_seconds()))
    return 0


def record_failed_attempt(key: str):
    ck = _count_key(key)
    st.session_state.setdefault(ck, 0)
    st.session_state[ck] += 1
    if st.session_state[ck] >= 5:
        st.session_state[_lockout_key(key)] = datetime.now() + timedelta(minutes=5)
        st.session_state[ck] = 0


def reset_failed_attempts(key: str):
    st.session_state[_count_key(key)] = 0
