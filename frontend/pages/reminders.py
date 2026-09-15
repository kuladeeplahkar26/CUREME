# pyrefly: ignore [missing-import]
import os
import sys
from datetime import datetime, timezone

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Daily Routine - MEMOAID", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id
role = st.session_state.role

st.markdown("""
<div style="margin-bottom: 24px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">schedule</span>
        <h1 style="color: #172536; font-size: 2rem; margin: 0;">Daily Routine & Schedule</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.05rem; margin: 0;">
        Clear, unhurried schedule of medications, meals, hydration, and restful activities.
    </p>
</div>
""", unsafe_allow_html=True)

icons = {
    "Medicine": "medication",
    "Meals": "restaurant",
    "Water": "water_drop",
    "Exercise": "fitness_center",
    "Doctor": "medical_services",
    "Family": "family_restroom",
    "Other": "event_note"
}


def load_reminders(uid):
    res = api.get_reminders(uid)
    if "error" in res:
        st.error(res["error"])
        return []
    return res


if role == "caregiver":
    elderly_users = api.get_all_elderly_users()
    if not elderly_users or (isinstance(elderly_users, dict) and "error" in elderly_users):
        st.info("No elderly participants registered yet.")
        st.stop()

    user_options = {f"{u['name']} (@{u['username']})": u['id'] for u in elderly_users}
    selected_user_str = st.selectbox("Select Participant to Manage", list(user_options.keys()))
    selected_user_id = user_options[selected_user_str]

    with st.expander("+ Schedule New Routine Task", expanded=False):
        with st.form("add_reminder_form"):
            task = st.text_input("Task / Medication Description", placeholder="e.g., Morning blood pressure tablet")
            rem_type = st.selectbox("Category", list(icons.keys()))
            date = st.date_input("Date")
            time = st.time_input("Time")

            if st.form_submit_button("Add to Schedule", type="primary"):
                if not task:
                    st.error("Please enter a description.")
                else:
                    res = api.add_reminder(selected_user_id, task, rem_type, str(date), str(time))
                    if "error" not in res:
                        st.success("Reminder added to schedule.")
                        st.rerun()

    reminders = load_reminders(selected_user_id)
else:
    reminders = load_reminders(user_id)

tab1, tab2 = st.tabs(["Today's Schedule", "All Records"])

today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

with tab1:
    today_rems = [r for r in reminders if r["date"] == today_str and r["status"] == "pending"]
    if not today_rems:
        st.markdown("""
            <div class="card" style="text-align: center; padding: 32px;">
                <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 36px; margin-bottom: 8px;">task_alt</span>
                <h4 style="color: #172536; margin: 0 0 4px 0;">All Caught Up!</h4>
                <p style="color: #6B7680; margin: 0;">No pending tasks remaining for today.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for r in sorted(today_rems, key=lambda x: x["time"]):
            icon_name = icons.get(r['reminder_type'], 'event_note')
            st.markdown(f"""
                <div class="card" style="padding: 20px 24px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <div style="width: 44px; height: 44px; border-radius: 10px; background-color: #DDF5EC; display: flex; align-items: center; justify-content: center;">
                                <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">{icon_name}</span>
                            </div>
                            <div>
                                <h3 style="margin: 0 0 2px 0; color: #172536; font-size: 1.15rem;">{r['time'][:5]} &mdash; {r['task']}</h3>
                                <span class="badge badge-green">{r['reminder_type']}</span>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Mark Complete", key=f"done_{r['id']}", type="primary"):
                api.mark_reminder_complete(r['id'])
                st.rerun()

with tab2:
    if not reminders:
        st.info("No routine records found.")
    else:
        for r in sorted(reminders, key=lambda x: (x["date"], x["time"]), reverse=True):
            icon_name = icons.get(r['reminder_type'], 'event_note')
            status_is_done = (r["status"] == "completed")
            status_badge = "badge-green" if status_is_done else "badge-yellow"
            status_text = "Completed" if status_is_done else "Pending"

            st.markdown(f"""
                <div class="card" style="padding: 16px 20px; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <span class="material-symbols-outlined" style="color: #6B7680; font-size: 22px;">{icon_name}</span>
                            <div>
                                <span style="font-size: 0.82rem; color: #6B7680; font-weight: 500;">{r['date']} at {r['time'][:5]}</span>
                                <h4 style="margin: 2px 0 0 0; color: #172536; font-size: 1.05rem;">{r['task']}</h4>
                            </div>
                        </div>
                        <span class="badge {status_badge}">{status_text}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if role == "caregiver":
                if st.button("Remove", key=f"del_{r['id']}"):
                    api.delete_reminder(r['id'])
                    st.rerun()

render_footer()
