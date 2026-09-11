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
from utils.data_service import get_recent_sessions, get_summary_stats, initialize_session_state

st.set_page_config(page_title="Your Progress - APON", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id

# Header
st.markdown("""
<div style="margin-bottom: 28px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">trending_up</span>
        <h1 style="color: #172536; font-size: 2.2rem; margin: 0;">Your Progress</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.15rem; margin: 0;">
        Review your memory practice, attention consistency, and daily milestone accomplishments.
    </p>
</div>
""", unsafe_allow_html=True)

# 4 Progress Summary Cards
stats = get_summary_stats(user_id)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Memory</div>
                <div class="stat-value" style="color: #1FA77A;">{stats['memory_practice']}</div>
            </div>
            <div class="stat-sub">+4% this week</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Attention</div>
                <div class="stat-value" style="color: #3478D4;">{stats['attention_score']}</div>
            </div>
            <div class="stat-sub" style="color: #3478D4;">Steady & focused</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="stat-card">
            <div>
                <div class="stat-label">Pattern Recognition</div>
                <div class="stat-value" style="color: #7B61D9;">85%</div>
            </div>
            <div class="stat-sub" style="color: #7B61D9;">Strong recall</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Consistency</div>
                <div class="stat-value" style="color: #F4C542;">{stats['current_streak']}</div>
            </div>
            <div class="stat-sub" style="color: #B58A00;">Active daily habit</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Weekly Activity & Performance Visualizations
col_chart1, col_chart2 = st.columns([3, 2])

with col_chart1:
    st.markdown("""
        <div class="card" style="padding-bottom: 8px;">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;">Accuracy Over Time</h3>
    """, unsafe_allow_html=True)

    # Fetch real trends from backend if available
    trends_data = []
    if user_id:
        try:
            res_trends = api.get_dashboard_trends(user_id)
            if res_trends and isinstance(res_trends, list) and len(res_trends) > 0:
                for t in res_trends:
                    trends_data.append({
                        "Date": t.get("date", "Recent"),
                        "Accuracy (%)": t.get("avg_accuracy", 75)
                    })
        except Exception:
            pass

    if not trends_data:
        trends_data = [
            {"Date": "Mon", "Accuracy (%)": 70},
            {"Date": "Tue", "Accuracy (%)": 75},
            {"Date": "Wed", "Accuracy (%)": 72},
            {"Date": "Thu", "Accuracy (%)": 82},
            {"Date": "Fri", "Accuracy (%)": 78},
            {"Date": "Sat", "Accuracy (%)": 85},
            {"Date": "Sun", "Accuracy (%)": 88},
        ]

    df_trends = pd.DataFrame(trends_data)
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
        height=260,
        font=dict(family="Inter", size=12, color="#6B7680"),
        xaxis=dict(gridcolor="#F0F3F5"),
        yaxis=dict(gridcolor="#F0F3F5", range=[50, 100])
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart2:
    st.markdown("""
        <div class="card" style="height: 330px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 12px;">Weekly Activity</h3>
                <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 20px;">Daily engagement status for this week.</p>
                
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background-color: #F5F7F8; border-radius: 12px; margin-bottom: 12px;">
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Mon</div><span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">check_circle</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Tue</div><span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">check_circle</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Wed</div><span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">check_circle</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Thu</div><span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">check_circle</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Fri</div><span class="material-symbols-outlined" style="color: #1FA77A; font-size: 22px;">check_circle</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Sat</div><span class="material-symbols-outlined" style="color: #E5E9EC; font-size: 22px;">radio_button_unchecked</span></div>
                    <div style="text-align: center;"><div style="font-weight: 600; font-size: 0.85rem;">Sun</div><span class="material-symbols-outlined" style="color: #E5E9EC; font-size: 22px;">radio_button_unchecked</span></div>
                </div>
            </div>
            
            <div style="background-color: #DDF5EC; border-radius: 10px; padding: 10px 14px; display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 20px;">emoji_events</span>
                <span style="color: #1FA77A; font-weight: 600; font-size: 0.88rem;">5-day goal reached! Keep it up.</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Recent Sessions Table
st.markdown("""
    <div class="card">
        <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;">Recent Sessions</h3>
""", unsafe_allow_html=True)

recent_sessions = get_recent_sessions(user_id)
df_sessions = pd.DataFrame(recent_sessions)
df_sessions.columns = ["Date & Time", "Activity Name", "Accuracy", "Duration"]

st.dataframe(
    df_sessions,
    use_container_width=True,
    hide_index=True
)

st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    if st.button("Practice Again", key="btn_practice_again", type="primary", use_container_width=True):
        st.switch_page("pages/games_menu.py")

st.markdown("</div>", unsafe_allow_html=True)

render_footer()
