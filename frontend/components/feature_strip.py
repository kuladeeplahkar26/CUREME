import streamlit as st

def render_feature_strip():
    st.markdown("""
        <div style="background-color: #183B20; border-radius: 16px; padding: 24px 32px; margin-top: -48px; margin-bottom: 48px; position: relative; z-index: 10; box-shadow: 0 4px 20px rgba(0,0,0,0.1); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 16px;">
            <div style="flex: 1; min-width: 200px; color: white;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="material-symbols-outlined" style="color: #F47A45; font-size: 20px;">psychology</span>
                    <h4 style="color: white; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.125rem;">Cognitive Exercises</h4>
                </div>
                <p style="color: #c2c9be; font-size: 0.875rem; margin: 0;">Adaptive recall & memory</p>
            </div>
            <div style="flex: 1; min-width: 200px; color: white;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="material-symbols-outlined" style="color: #F47A45; font-size: 20px;">favorite</span>
                    <h4 style="color: white; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.125rem;">Personalized Care</h4>
                </div>
                <p style="color: #c2c9be; font-size: 0.875rem; margin: 0;">Paced for calm comfort</p>
            </div>
            <div style="flex: 1; min-width: 200px; color: white;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="material-symbols-outlined" style="color: #F47A45; font-size: 20px;">trending_up</span>
                    <h4 style="color: white; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.125rem;">Progress Tracking</h4>
                </div>
                <p style="color: #c2c9be; font-size: 0.875rem; margin: 0;">Clarity without stress</p>
            </div>
            <div style="flex: 1; min-width: 200px; color: white;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span class="material-symbols-outlined" style="color: #F47A45; font-size: 20px;">record_voice_over</span>
                    <h4 style="color: white; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.125rem;">Voice Assistance</h4>
                </div>
                <p style="color: #c2c9be; font-size: 0.875rem; margin: 0;">Gentle audio guidance</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
