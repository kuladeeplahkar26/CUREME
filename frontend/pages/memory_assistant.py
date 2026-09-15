# pyrefly: ignore [missing-import]
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Memory Assistant - MEMOAID", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id

st.markdown("""
<div style="margin-bottom: 24px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">psychology</span>
        <h1 style="color: #172536; font-size: 2.2rem; margin: 0;">Memory Assistant</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.15rem; margin: 0;">
        A simple companion for everyday reminders and memory support.
    </p>
</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state or not st.session_state.chat_history:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Good morning. Would you like to start today's activity?"}
    ]

tab1, tab2 = st.tabs(["Conversation", "Stored Memories"])

with tab1:
    st.markdown('<div class="card" style="padding: 24px; min-height: 400px; display: flex; flex-direction: column; justify-content: space-between;">', unsafe_allow_html=True)
    
    # Message display area
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
                <div style="background-color: #1FA77A; color: white; padding: 12px 18px; border-radius: 16px 16px 4px 16px; margin-bottom: 12px; max-width: 70%; float: right; clear: both; font-size: 1.05rem; line-height: 1.5; box-shadow: 0 2px 8px rgba(31, 167, 122, 0.2);">
                    {msg['content']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #F5F7F8; color: #17212B; padding: 12px 18px; border-radius: 16px 16px 16px 4px; margin-bottom: 12px; max-width: 70%; float: left; clear: both; font-size: 1.05rem; line-height: 1.5; border: 1px solid #E5E9EC;">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #1FA77A; margin-bottom: 2px;">MEMOAID Assistant</div>
                    {msg['content']}
                </div>
            """, unsafe_allow_html=True)
    st.markdown('<div style="clear: both;"></div></div>', unsafe_allow_html=True)

    # Chat Input Form
    with st.form("assistant_chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_msg = st.text_input("Message", placeholder="Type a message...", label_visibility="collapsed")
        with col_send:
            send_btn = st.form_submit_button("Send", type="primary", use_container_width=True)

        if send_btn and user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            try:
                res = api.ask_memory_question(user_id, user_msg)
                if isinstance(res, dict) and "answer" in res and res["answer"]:
                    bot_answer = res["answer"]
                else:
                    bot_answer = "I'm right here with you. Would you like to practice a cognitive exercise together?"
            except Exception:
                bot_answer = "Your assistant is currently unavailable. You can still continue with cognitive activities."

            st.session_state.chat_history.append({"role": "assistant", "content": bot_answer})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("""
        <div class="card">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 8px;">Personal Memory Journal</h3>
            <p style="color: #6B7680; font-size: 0.95rem; margin-bottom: 20px;">Cherished family details, friends, and special moments recorded for easy recall.</p>
    """, unsafe_allow_html=True)

    mems = api.get_memories(user_id)
    if not mems or (isinstance(mems, dict) and "error" in mems):
        st.info("No personal memories recorded yet. You can add one below.")
    else:
        for m in mems:
            st.markdown(f"""
                <div style="background-color: #F5F7F8; border-left: 4px solid #1FA77A; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                        <strong style="color: #17212B; font-size: 1.05rem;">{m.get('person_name', m.get('topic', 'Memory'))}</strong>
                        <span style="color: #1FA77A; font-size: 0.85rem; font-weight: 600;">{m.get('relationship', 'Family / Personal')}</span>
                    </div>
                    <p style="color: #6B7680; margin: 0; font-size: 0.95rem;">{m.get('information', m.get('content', ''))}</p>
                </div>
            """, unsafe_allow_html=True)

    with st.expander("Add a New Memory to Journal"):
        with st.form("add_memory_form"):
            p_name = st.text_input("Person or Topic", placeholder="e.g. Family member or childhood memory")
            p_rel = st.text_input("Relationship or Context", placeholder="e.g. Granddaughter, lives in Boston")
            p_info = st.text_area("Details to Remember", placeholder="e.g. Loves painting watercolor landscapes and visits on Sundays.")
            submit_mem = st.form_submit_button("Save Memory", type="primary")

            if submit_mem:
                if not p_name or not p_info:
                    st.error("Please enter both a topic/name and memory details.")
                else:
                    res = api.add_memory(user_id, p_name, p_rel, p_info)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success("Memory successfully saved to your journal!")
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
