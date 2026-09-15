import streamlit as st

def render_about_section():
    st.markdown("""
        <div style="margin-top: 48px; margin-bottom: 48px; padding: 24px;">
            <div style="margin-bottom: 24px;">
                <span style="color: #F47A45; font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">ABOUT MEMOAID</span>
            </div>
            <h2 class="editorial-heading" style="font-size: 2rem !important; margin-top: 0;">Technology Designed Around People</h2>
            <p style="font-size: 1.25rem !important; color: #424940; max-width: 800px; line-height: 1.6;">
                MEMOAID combines cognitive activities, adaptive experiences, and caregiver support in a simple interface. We emphasize zero-frustration interfaces, large tap targets, high contrast, and clinically validated recall stimulation to provide a dignified experience for our users.
            </p>
            
            <div style="margin-top: 32px; background-color: #FFFFFF; border-radius: 16px; padding: 24px; border: 1.5px solid rgba(244, 122, 69, 0.3); border-left: 6px solid #F47A45; box-shadow: 0 4px 12px rgba(244, 122, 69, 0.05); display: inline-block;">
                <h4 style="margin: 0 0 8px 0; color: #244D2A;">Simple • Accessible • Personalized</h4>
                <p style="margin: 0; color: #687064; font-size: 1rem;">98% caregiver reassurance rate.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
