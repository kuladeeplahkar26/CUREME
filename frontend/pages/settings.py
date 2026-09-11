# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Settings - NEUROVIA", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_name = st.session_state.get("name", "User")
user_role = st.session_state.get("role", "elderly")

st.markdown("""
<div style="margin-bottom: 28px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">settings</span>
        <h1 style="color: #172536; font-size: 2.2rem; margin: 0;">Settings & Preferences</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.15rem; margin: 0;">
        Personalize your reading comfort, visual accessibility, and account details.
    </p>
</div>
""", unsafe_allow_html=True)

col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;'>Visual & Accessibility Controls</h3>", unsafe_allow_html=True)

    with st.form("settings_form"):
        current_text_size = st.session_state.get("text_size", "Standard")
        text_size_idx = 0 if current_text_size == "Standard" else 1
        new_text_size = st.radio(
            "Display Font Size",
            ["Standard", "Large"],
            index=text_size_idx,
            help="Large increases headline and body font sizes across all screens for enhanced legibility."
        )

        current_contrast = st.session_state.get("contrast", "Standard")
        contrast_idx = 0 if current_contrast == "Standard" else 1
        new_contrast = st.radio(
            "Display Contrast",
            ["Standard", "High"],
            index=contrast_idx,
            help="High contrast maximizes border clarity and contrast ratios."
        )

        current_voice = st.session_state.get("voice_enabled", False)
        new_voice = st.checkbox(
            "Enable Voice Assistance & Audio Reading",
            value=current_voice,
            help="Provides gentle voice reading for exercise prompts and instructions."
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("Save Preferences", type="primary")

        if save_btn:
            st.session_state.text_size = new_text_size
            st.session_state.contrast = new_contrast
            st.session_state.voice_enabled = new_voice
            st.success("Preferences successfully saved and applied!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with col_side:
    st.markdown(f"""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 12px;">Active Profile</h3>
            <div style="margin-bottom: 12px;">
                <div style="color: #6B7680; font-size: 0.85rem;">Display Name</div>
                <div style="color: #17212B; font-weight: 600; font-size: 1.1rem;">{user_name}</div>
            </div>
            <div style="margin-bottom: 16px;">
                <div style="color: #6B7680; font-size: 0.85rem;">Current Role</div>
                <div style="color: #1FA77A; font-weight: 600; font-size: 1rem;">{user_role.capitalize()}</div>
            </div>
            <div style="border-top: 1px solid #E5E9EC; padding-top: 16px;">
                <p style="color: #6B7680; font-size: 0.85rem; margin: 0;">
                    NEUROVIA stores your cognitive exercise results locally and securely. No personal medical information is shared externally.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out of NEUROVIA", key="btn_settings_signout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

render_footer()
