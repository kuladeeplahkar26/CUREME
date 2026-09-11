import streamlit as st


def render_footer():
    st.markdown("""
        <div style="margin-top: 64px; padding: 32px 0 24px 0; border-top: 1px solid #E5E9EC; text-align: center;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 20px;">spa</span>
                <span style="font-weight: 700; color: #17212B; font-size: 1.1rem; letter-spacing: -0.01em;">NEUROVIA</span>
            </div>
            
            <div style="max-width: 650px; margin: 0 auto 16px auto; background-color: #FFFFFF; border: 1px solid #E5E9EC; border-radius: 12px; padding: 14px 20px;">
                <p style="color: #6B7680; font-size: 0.85rem; margin: 0; line-height: 1.5;">
                    <strong>Medical Disclaimer:</strong> NEUROVIA is a cognitive wellness and assistance platform. It does not diagnose, treat, or replace professional medical care.
                </p>
            </div>
            
            <p style="color: #9AA4AC; font-size: 0.8rem; margin: 0;">
                &copy; 2026 NEUROVIA Cognitive Care. All rights reserved.
            </p>
        </div>
    """, unsafe_allow_html=True)
