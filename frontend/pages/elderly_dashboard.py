# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import get_summary_stats, initialize_session_state

st.set_page_config(page_title="APON - Home", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id
user_name = st.session_state.get("name", "Friend")

# Header Section (Section 8)
greeting_title = f"Good morning, {user_name}" if user_name != "Friend" else "Good morning"
st.markdown(f"""
<div style="margin-bottom: 28px;">
    <h1 style="color: #172536; font-size: 2.2rem; margin-bottom: 6px;">{greeting_title}</h1>
    <p style="color: #6B7680; font-size: 1.15rem; margin: 0;">Let's make today's memory journey a little easier.</p>
</div>
""", unsafe_allow_html=True)

# 4 Summary Statistics Cards (Section 9)
stats = get_summary_stats(user_id)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Today's Activities</div>
                <div class="stat-value">{stats['activities_today']}</div>
            </div>
            <div class="stat-sub">{stats['activities_sub']}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Memory Practice</div>
                <div class="stat-value" style="color: #1FA77A;">{stats['memory_practice']}</div>
            </div>
            <div class="stat-sub">{stats['memory_sub']}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Attention</div>
                <div class="stat-value" style="color: #3478D4;">{stats['attention_score']}</div>
            </div>
            <div class="stat-sub" style="color: #3478D4;">{stats['attention_sub']}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-label">Current Streak</div>
                <div class="stat-value" style="color: #F4C542;">{stats['current_streak']}</div>
            </div>
            <div class="stat-sub" style="color: #B58A00;">{stats['streak_sub']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# 3 Main Dashboard Cards (Section 10)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
        <div class="card" style="min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="badge badge-green">Recommended Activity</span>
                    <span style="color: #6B7680; font-size: 0.85rem;">3 min</span>
                </div>
                <h3 style="color: #172536; margin: 0 0 8px 0;">Today's Cognitive Activity</h3>
                <p style="color: #17212B; font-weight: 600; font-size: 1.1rem; margin-bottom: 4px;">Memory Match</p>
                <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 16px;">Pair familiar household items and pictures to gently train visual memory recall.</p>
                <div style="font-size: 0.85rem; color: #1FA77A; font-weight: 600; margin-bottom: 16px;">Difficulty: Easy (Level 1)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Start Activity", key="btn_start_act", use_container_width=True, type="primary"):
        st.switch_page("pages/game_memory_match.py")

with c2:
    st.markdown("""
        <div class="card" style="min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="badge badge-blue">Everyday Support</span>
                    <span class="material-symbols-outlined" style="color: #3478D4; font-size: 20px;">psychology</span>
                </div>
                <h3 style="color: #172536; margin: 0 0 8px 0;">Memory Assistant</h3>
                <p style="color: #17212B; font-weight: 600; font-size: 1.1rem; margin-bottom: 4px;">Need help remembering something?</p>
                <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 16px;">Ask questions about your daily schedule, medication times, or personal memories in a calm conversation.</p>
                <div style="font-size: 0.85rem; color: #3478D4; font-weight: 600; margin-bottom: 16px;">Ready to help anytime</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Open Assistant", key="btn_open_asst", use_container_width=True):
        st.switch_page("pages/memory_assistant.py")

with c3:
    st.markdown("""
        <div class="card" style="min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="badge badge-yellow">Weekly Insights</span>
                    <span class="material-symbols-outlined" style="color: #F4C542; font-size: 20px;">insights</span>
                </div>
                <h3 style="color: #172536; margin: 0 0 8px 0;">Caregiver Overview</h3>
                <p style="color: #17212B; font-weight: 600; font-size: 1.1rem; margin-bottom: 4px;">Recent Activity Summary</p>
                <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 16px;">View detailed participation trends, routine completion rates, and cognitive engagement history.</p>
                <div style="font-size: 0.85rem; color: #B58A00; font-weight: 600; margin-bottom: 16px;">Updated today</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View Progress", key="btn_view_prog", use_container_width=True):
        st.switch_page("pages/progress.py")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Adaptive Difficulty / Live Recommendation Card (Section 17)
rec_res = api.get_recommendation(user_id) if user_id else {}
if isinstance(rec_res, dict) and "recommendation" in rec_res:
    rec_text = rec_res["recommendation"]
else:
    rec_text = "Personalized recommendations will appear as more session data becomes available."

st.markdown(f"""
    <div class="card" style="border-left: 4px solid #1FA77A; padding: 20px 24px; display: flex; align-items: center; gap: 16px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 28px;">lightbulb</span>
        <div>
            <h4 style="margin: 0 0 4px 0; color: #172536; font-size: 1.1rem;">Personalized Focus Recommendation</h4>
            <p style="margin: 0; color: #6B7680; font-size: 0.98rem;">{rec_text}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

render_footer()
