import streamlit as st

def render_hero():
    st.markdown("""
        <div style="background-color: #244D2A; border-radius: 24px; padding: 48px 32px; color: white; display: flex; flex-direction: column; gap: 24px; margin-bottom: 24px; box-shadow: 0 12px 32px -4px rgba(36, 51, 35, 0.12);">
            <div>
                <span style="background-color: rgba(244, 122, 69, 0.15); color: #F47A45; padding: 6px 12px; border-radius: 16px; font-size: 0.875rem; font-weight: 700; border: 1px solid #F47A45; text-transform: uppercase; letter-spacing: 0.05em;">PERSONALIZED COGNITIVE CARE</span>
            </div>
            <h1 style="color: white !important; font-size: 3rem !important; line-height: 1.2 !important; margin: 0;">Helping Every Memory<br/>Stay Connected.</h1>
            <p style="color: #F7F6F1 !important; font-size: 1.25rem !important; max-width: 600px; opacity: 0.9; margin: 0;">
                Compassionate, clinically-guided AI cognitive exercises and voice memory support designed with dignity for seniors and peace of mind for families.
            </p>
        </div>
    """, unsafe_allow_html=True)
