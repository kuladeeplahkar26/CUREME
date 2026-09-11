# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import styles
from utils.data_service import initialize_session_state

st.set_page_config(page_title="APON - Cognitive Wellness Platform", layout="wide")
initialize_session_state()
styles.apply_styles()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")
else:
    role = st.session_state.get("role", "elderly")
    if role == "elderly":
        st.switch_page("pages/elderly_dashboard.py")
    else:
        st.switch_page("pages/caregiver_dashboard.py")
