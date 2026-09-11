# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.footer import render_footer
from utils import styles
from utils.api_client import api
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Sign In - APON", layout="centered")
initialize_session_state()
styles.apply_styles()

# APON Header
st.markdown("""
<div style="text-align: center; margin-top: 24px; margin-bottom: 28px;">
    <div style="display: inline-flex; align-items: center; gap: 10px; background: #1D2B3A; color: white; padding: 10px 20px; border-radius: 12px; margin-bottom: 16px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 24px;">spa</span>
        <span style="font-weight: 700; font-size: 1.3rem; letter-spacing: -0.01em;">APON</span>
    </div>
    <h1 style="color: #172536; font-size: 2.2rem; margin-bottom: 8px;">Cognitive Wellness Platform</h1>
    <p style="color: #6B7680; font-size: 1.05rem; max-width: 480px; margin: 0 auto;">Sign in to access personalized memory support, cognitive activities, and caregiver insights.</p>
</div>
""", unsafe_allow_html=True)

# Main Authentication Form Card
login_card = st.container(border=True)
with login_card:
    with st.form("signin_form"):
        st.markdown("<h3 style='color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 16px;'>Sign In</h3>", unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            login_elderly = st.form_submit_button("Elderly Patient Login", type="primary", use_container_width=True)
        with col_btn2:
            login_caregiver = st.form_submit_button("Caregiver Login", type="secondary", use_container_width=True)
        
        if login_elderly or login_caregiver:
            target_role = "elderly" if login_elderly else "caregiver"
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Signing in..."):
                    res = api.login(username, password)
                    
                    if "error" in res:
                        st.error("Invalid username or password. If you do not have an account, register below.")
                    else:
                        st.session_state.user_id = res["user_id"]
                        st.session_state.role = target_role
                        st.session_state.name = res["name"]
                        
                        if target_role == "elderly":
                            st.switch_page("pages/elderly_dashboard.py")
                        else:
                            st.switch_page("pages/caregiver_dashboard.py")

# Clean, unintrusive New Account registration expander
with st.expander("New to APON? Create your account"):
    with st.form("register_form"):
        st.markdown("<h4 style='color: #172536; margin-top: 0;'>Create a New Account</h4>", unsafe_allow_html=True)
        
        reg_name = st.text_input("Full Name", placeholder="Enter full name")
        role_choice = st.radio("Account Role", ["Participant (Elderly)", "Caregiver / Family"], horizontal=True)
        selected_role = "elderly" if "Elderly" in role_choice else "caregiver"
        
        reg_age = st.number_input("Age", min_value=1, max_value=120, value=70 if selected_role == "elderly" else 40, step=1)
        reg_username = st.text_input("Choose Username", placeholder="Choose your username")
        reg_password = st.text_input("Choose Password", type="password", placeholder="Create your password")
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        reg_submitted = st.form_submit_button("Create Account & Sign In", type="primary", use_container_width=True)
        
        if reg_submitted:
            if not reg_name or not reg_username or not reg_password:
                st.error("Please fill in all required fields.")
            else:
                with st.spinner("Creating your account..."):
                    reg_res = api.register(
                        username=reg_username,
                        password=reg_password,
                        name=reg_name,
                        age=int(reg_age),
                        role=selected_role
                    )
                    
                    if "error" in reg_res:
                        st.error(reg_res["error"])
                    else:
                        login_res = api.login(reg_username, reg_password)
                        if "error" not in login_res:
                            st.session_state.user_id = login_res["user_id"]
                            st.session_state.role = login_res["role"]
                            st.session_state.name = login_res["name"]
                            st.success("Account created successfully! Redirecting...")
                            
                            if login_res["role"] == "elderly":
                                st.switch_page("pages/elderly_dashboard.py")
                            else:
                                st.switch_page("pages/caregiver_dashboard.py")
                        else:
                            st.success("Account created. Please sign in above.")

render_footer()
