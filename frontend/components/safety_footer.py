import streamlit as st


def render_safety_footer():
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #687064; font-size: 14px; padding: 10px;'>
            <b>Safety Notice:</b> This application supports cognitive engagement and caregiver monitoring only.
            It does not replace professional medical advice. Game scores reflect activity, not a health assessment.
        </div>
    """, unsafe_allow_html=True)
