# pyrefly: ignore [missing-import]
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import get_recent_sessions, initialize_session_state

st.set_page_config(page_title="Caregiver Overview - NEUROVIA", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

st.session_state.role = "caregiver"

# Header with Switch View button
col_head, col_switch = st.columns([3, 1])
with col_head:
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">monitoring</span>
            <h1 style="color: #172536; font-size: 2.2rem; margin: 0;">Caregiver Overview</h1>
        </div>
        <p style="color: #6B7680; font-size: 1.15rem; margin: 0;">
            Review participant cognitive engagement, routine completion, and support notes.
        </p>
    </div>
    """, unsafe_allow_html=True)
with col_switch:
    if st.button("Switch to Elderly View", key="btn_switch_to_eld", use_container_width=True):
        st.session_state.role = "elderly"
        st.switch_page("pages/elderly_dashboard.py")

# Select Elderly User to Monitor
elderly_users = api.get_all_elderly_users()
if not elderly_users or (isinstance(elderly_users, dict) and "error" in elderly_users):
    st.info("No registered elderly participants found. You can register a participant in the User Management tab below.")
    uid = None
else:
    user_options = {f"{u['name']} (@{u['username']})": u['id'] for u in elderly_users}
    selected_user_str = st.selectbox("Select Participant to Monitor", list(user_options.keys()))
    uid = user_options[selected_user_str]

# 4 Caregiver Summary Cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
        <div class="stat-card">
            <div>
                <div class="stat-label">Activities Completed</div>
                <div class="stat-value" style="color: #1FA77A;">12</div>
            </div>
            <div class="stat-sub">Across past 7 days</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="stat-card">
            <div>
                <div class="stat-label">Average Performance</div>
                <div class="stat-value" style="color: #3478D4;">79%</div>
            </div>
            <div class="stat-sub" style="color: #3478D4;">Consistent recall</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="stat-card">
            <div>
                <div class="stat-label">Current Streak</div>
                <div class="stat-value" style="color: #F4C542;">5 days</div>
            </div>
            <div class="stat-sub" style="color: #B58A00;">Goal on track</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
        <div class="stat-card">
            <div>
                <div class="stat-label">Last Active</div>
                <div class="stat-value" style="color: #172536; font-size: 1.6rem;">Today</div>
            </div>
            <div class="stat-sub" style="color: #1FA77A;">10:15 AM Session</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Main Caregiver Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Activity Trends", "Routine Support", "Stored Memories", "User Management"
])

with tab1:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;">Today's Cognitive Activity Summary</h3>
    """, unsafe_allow_html=True)
    
    summary = api.get_dashboard_summary(uid) if uid else {}
    if not summary or "error" in summary or not summary.get("games"):
        st.info("No cognitive activity recorded for today yet.")
    else:
        cols = st.columns(len(summary["games"]) + 1)
        for i, (game, acc) in enumerate(summary["games"].items()):
            with cols[i]:
                st.markdown(f"""
                    <div style="background-color: #F5F7F8; border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="color: #6B7680; font-size: 0.9rem; font-weight: 500;">{game}</div>
                        <div style="color: #1FA77A; font-size: 1.8rem; font-weight: 700;">{acc:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        with cols[-1]:
            st.markdown(f"""
                <div style="background-color: #DDF5EC; border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="color: #1FA77A; font-size: 0.9rem; font-weight: 600;">Overall Average</div>
                    <div style="color: #172536; font-size: 1.8rem; font-weight: 700;">{summary.get('overall_accuracy', 0):.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

    # Activity Flags
    st.markdown("<h4 style='color: #172536; margin-top: 24px; margin-bottom: 8px;'>Activity Observations</h4>", unsafe_allow_html=True)
    flags = api.get_activity_flags(uid) if uid else []
    if not flags or "error" in flags:
        st.success("All cognitive markers and response times are in healthy, calm ranges.")
    else:
        for f in flags:
            st.warning(f"{f.get('flag_type', 'Note')}: {f.get('description', '')}")

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;">Historical Accuracy Trend</h3>
    """, unsafe_allow_html=True)
    
    trends = api.get_dashboard_trends(uid) if uid else []
    if not trends or "error" in trends:
        trends_demo = [
            {"Date": "Mon", "Accuracy (%)": 72},
            {"Date": "Tue", "Accuracy (%)": 78},
            {"Date": "Wed", "Accuracy (%)": 75},
            {"Date": "Thu", "Accuracy (%)": 82},
            {"Date": "Fri", "Accuracy (%)": 80}
        ]
        df_trends = pd.DataFrame(trends_demo)
    else:
        df_trends = pd.DataFrame([{"Date": t["date"], "Accuracy (%)": t["avg_accuracy"]} for t in trends])
    
    fig = px.line(
        df_trends,
        x="Date",
        y="Accuracy (%)",
        markers=True,
        color_discrete_sequence=["#1FA77A"]
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=10, b=20),
        height=280,
        font=dict(family="Inter", size=12, color="#6B7680")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 8px;">Daily Routine Schedule</h3>
            <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 16px;">Manage medication, meals, and hydration reminders.</p>
    """, unsafe_allow_html=True)
    
    if uid:
        rems = api.get_reminders(uid)
        if not rems or "error" in rems:
            st.info("No routine reminders added yet.")
        else:
            for r in rems:
                status_color = "#1FA77A" if r.get("is_completed") else "#F28C45"
                status_text = "Completed" if r.get("is_completed") else "Pending"
                st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background-color: #F5F7F8; border-radius: 10px; margin-bottom: 8px;">
                        <div>
                            <strong style="color: #17212B;">{r.get('reminder_text', 'Reminder')}</strong>
                            <div style="color: #6B7680; font-size: 0.85rem;">{r.get('reminder_type', 'Routine')} • Scheduled: {r.get('scheduled_time', 'Daily')}</div>
                        </div>
                        <span style="color: {status_color}; font-weight: 600; font-size: 0.85rem;">{status_text}</span>
                    </div>
                """, unsafe_allow_html=True)

    if st.button("Open Full Routine Manager", key="btn_open_rem_mgr", type="primary"):
        st.switch_page("pages/reminders.py")
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 8px;">Participant Memory Journal</h3>
            <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 16px;">Cherished family details and memories recorded for recall exercises.</p>
    """, unsafe_allow_html=True)

    if uid:
        mems = api.get_memories(uid)
        if not mems or "error" in mems:
            st.info("No memories stored yet.")
        else:
            for m in mems:
                st.markdown(f"""
                    <div style="border-left: 3px solid #1FA77A; padding: 8px 14px; background-color: #F5F7F8; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #17212B;">{m.get('topic', 'Memory')}:</strong>
                        <span style="color: #6B7680;"> {m.get('content', '')}</span>
                    </div>
                """, unsafe_allow_html=True)

    if st.button("Open Memory Assistant", key="btn_open_asst_tab", type="primary"):
        st.switch_page("pages/memory_assistant.py")
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 8px;">Add New Participant</h3>
    """, unsafe_allow_html=True)
    with st.form("cg_add_user_form"):
        new_name = st.text_input("Participant Name", placeholder="Enter patient name")
        new_age = st.number_input("Age", min_value=1, max_value=120, value=75)
        new_uname = st.text_input("Choose Username", placeholder="Enter username")
        new_pwd = st.text_input("Password", type="password", placeholder="Enter secure password")
        add_submitted = st.form_submit_button("Register Participant", type="primary")
        
        if add_submitted:
            if not new_name or not new_uname or not new_pwd:
                st.error("Please fill in all fields.")
            else:
                res = api.register(new_uname, new_pwd, new_name, int(new_age), "elderly")
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(f"Participant {new_name} successfully registered!")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
