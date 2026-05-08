from supabase import create_client, Client
import streamlit as st
from datetime import datetime, timezone, timedelta
import pytz


def get_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_tz() -> pytz.BaseTzInfo:
    return pytz.timezone(st.secrets.get("TIMEZONE", "America/New_York"))


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

def get_active_employees() -> list:
    return get_client().table("employees").select("id, name").eq("is_active", True).order("name").execute().data


def get_all_employees() -> list:
    return get_client().table("employees").select("*").order("name").execute().data


def get_employee_by_name(name: str) -> dict | None:
    result = get_client().table("employees").select("*").eq("name", name).eq("is_active", True).execute()
    return result.data[0] if result.data else None


def get_employee_by_id(employee_id: str) -> dict | None:
    result = get_client().table("employees").select("*").eq("id", employee_id).execute()
    return result.data[0] if result.data else None


def add_employee(name: str, password_hash: str) -> dict:
    return get_client().table("employees").insert({"name": name, "password_hash": password_hash}).execute().data[0]


def update_employee_password(employee_id: str, password_hash: str):
    get_client().table("employees").update({"password_hash": password_hash}).eq("id", employee_id).execute()


def set_employee_active(employee_id: str, active: bool):
    get_client().table("employees").update({"is_active": active}).eq("id", employee_id).execute()


# ---------------------------------------------------------------------------
# Clock in / out
# ---------------------------------------------------------------------------

def is_clocked_in(employee_id: str) -> bool:
    result = get_client().table("time_entries").select("id").eq("employee_id", employee_id).is_("clock_out", "null").execute()
    return len(result.data) > 0


def get_open_entry(employee_id: str) -> dict | None:
    result = (
        get_client()
        .table("time_entries")
        .select("id, clock_in")
        .eq("employee_id", employee_id)
        .is_("clock_out", "null")
        .order("clock_in", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def clock_in(employee_id: str):
    now = datetime.now(timezone.utc).isoformat()
    get_client().table("time_entries").insert({"employee_id": employee_id, "clock_in": now}).execute()


def clock_out(employee_id: str) -> bool:
    entry = get_open_entry(employee_id)
    if not entry:
        return False
    now = datetime.now(timezone.utc).isoformat()
    get_client().table("time_entries").update({"clock_out": now}).eq("id", entry["id"]).execute()
    return True


def get_currently_clocked_in() -> list:
    result = (
        get_client()
        .table("time_entries")
        .select("id, clock_in, employees(id, name)")
        .is_("clock_out", "null")
        .execute()
    )
    return [
        {
            "entry_id": r["id"],
            "employee_id": r["employees"]["id"],
            "employee_name": r["employees"]["name"],
            "clock_in": datetime.fromisoformat(r["clock_in"]),
        }
        for r in result.data
    ]


def force_clock_out(entry_id: str):
    now = datetime.now(timezone.utc).isoformat()
    get_client().table("time_entries").update({"clock_out": now}).eq("id", entry_id).execute()


# ---------------------------------------------------------------------------
# Time entries
# ---------------------------------------------------------------------------

def get_time_entries(employee_id: str | None = None, start_date=None, end_date=None) -> list:
    q = get_client().table("time_entries").select("id, clock_in, clock_out, employee_id, employees(name)")
    if employee_id:
        q = q.eq("employee_id", employee_id)
    if start_date:
        q = q.gte("clock_in", start_date.isoformat())
    if end_date:
        q = q.lt("clock_in", (end_date + timedelta(days=1)).isoformat())
    return q.order("clock_in", desc=True).execute().data


def update_time_entry(entry_id: str, clock_in: datetime, clock_out: datetime | None):
    data = {"clock_in": clock_in.isoformat()}
    data["clock_out"] = clock_out.isoformat() if clock_out else None
    get_client().table("time_entries").update(data).eq("id", entry_id).execute()


def delete_time_entry(entry_id: str):
    get_client().table("time_entries").delete().eq("id", entry_id).execute()
