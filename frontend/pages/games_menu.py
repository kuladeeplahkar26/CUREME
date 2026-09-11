# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.data_service import get_activities_catalog, initialize_session_state

st.set_page_config(page_title="Cognitive Activities - APON", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

# Section Heading
st.markdown("""
<div style="margin-bottom: 32px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">psychology</span>
        <h1 style="color: #172536; font-size: 2.2rem; margin: 0;">Cognitive Activities</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.15rem; margin: 0; max-width: 680px;">
        Simple activities designed to exercise memory, attention and everyday recall in a relaxed, encouraging environment.
    </p>
</div>
""", unsafe_allow_html=True)

activities = get_activities_catalog()

# Render 3 columns on first row, 2 columns on second row
cols_row1 = st.columns(3)
for idx in range(3):
    act = activities[idx]
    with cols_row1[idx]:
        st.markdown(f"""
            <div class="card" style="min-height: 290px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                        <div style="width: 44px; height: 44px; border-radius: 10px; background-color: #F5F7F8; display: flex; align-items: center; justify-content: center;">
                            <span class="material-symbols-outlined" style="color: {act['color']}; font-size: 24px;">{act['icon']}</span>
                        </div>
                        <span class="badge {act['badge_class']}">{act['difficulty']}</span>
                    </div>
                    <h3 style="color: #172536; font-size: 1.25rem; margin: 0 0 6px 0;">{act['name']}</h3>
                    <p style="color: #6B7680; font-size: 0.95rem; min-height: 48px; margin-bottom: 12px;">{act['description']}</p>
                    <div style="color: #9AA4AC; font-size: 0.85rem; margin-bottom: 16px;">Estimated: <strong>{act['duration']}</strong></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"Play {act['name']}", key=f"btn_play_{act['id']}", use_container_width=True, type="primary"):
            st.session_state.selected_game = act["name"]
            st.switch_page(act["route"])

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

cols_row2 = st.columns([1, 1, 1])
for idx in range(3, len(activities)):
    act = activities[idx]
    with cols_row2[idx - 3]:
        st.markdown(f"""
            <div class="card" style="min-height: 290px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                        <div style="width: 44px; height: 44px; border-radius: 10px; background-color: #F5F7F8; display: flex; align-items: center; justify-content: center;">
                            <span class="material-symbols-outlined" style="color: {act['color']}; font-size: 24px;">{act['icon']}</span>
                        </div>
                        <span class="badge {act['badge_class']}">{act['difficulty']}</span>
                    </div>
                    <h3 style="color: #172536; font-size: 1.25rem; margin: 0 0 6px 0;">{act['name']}</h3>
                    <p style="color: #6B7680; font-size: 0.95rem; min-height: 48px; margin-bottom: 12px;">{act['description']}</p>
                    <div style="color: #9AA4AC; font-size: 0.85rem; margin-bottom: 16px;">Estimated: <strong>{act['duration']}</strong></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"Play {act['name']}", key=f"btn_play_{act['id']}", use_container_width=True, type="primary"):
            st.session_state.selected_game = act["name"]
            st.switch_page(act["route"])

# Empty space in 3rd column for balance
with cols_row2[2]:
    st.markdown("""
        <div class="card" style="min-height: 290px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-style: dashed; background-color: transparent;">
            <span class="material-symbols-outlined" style="color: #9AA4AC; font-size: 36px; margin-bottom: 10px;">add_circle</span>
            <h4 style="color: #6B7680; margin: 0 0 6px 0;">More Activities</h4>
            <p style="color: #9AA4AC; font-size: 0.9rem; max-width: 220px; margin: 0 0 16px 0;">New exercises are tailored as your cognitive profile grows.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View Your Progress", key="btn_explore_prog", use_container_width=True):
        st.switch_page("pages/progress.py")

render_footer()
