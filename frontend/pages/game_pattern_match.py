# pyrefly: ignore [missing-import]
import os
import sys
import time

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Pattern Recall - NEUROVIA", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id

st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
        <span class="material-symbols-outlined" style="color: #3478D4; font-size: 32px;">grid_view</span>
        <h1 style="color: #172536; font-size: 2rem; margin: 0;">Pattern Recall</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.05rem; margin: 0;">
        Observe the pattern sequence carefully and select the missing element that completes it.
    </p>
</div>
""", unsafe_allow_html=True)

if "pm_state" not in st.session_state:
    difficulty_res = api.get_current_difficulty(user_id, "Pattern Match")
    st.session_state.pm_state = {
        "difficulty_level": difficulty_res.get("difficulty_level", 1) if "error" not in difficulty_res else 1,
        "start_time": time.time(),
        "q_index": 0,
        "correct": 0,
        "game_over": False
    }

state = st.session_state.pm_state

PATTERNS_BY_LEVEL = {
    1: [
        {"p": "Red • Blue • Red • Blue • Red • ?", "opts": ["Red", "Blue", "Green", "Yellow"], "ans": "Blue"},
        {"p": "Circle • Square • Circle • Square • Circle • ?", "opts": ["Circle", "Square", "Triangle", "Star"], "ans": "Square"},
        {"p": "Day • Night • Day • Night • Day • ?", "opts": ["Day", "Night", "Dusk", "Dawn"], "ans": "Night"},
        {"p": "Up • Down • Up • Down • Up • ?", "opts": ["Up", "Down", "Left", "Right"], "ans": "Down"},
        {"p": "1 • 2 • 1 • 2 • 1 • ?", "opts": ["1", "2", "3", "4"], "ans": "2"},
    ],
    2: [
        {"p": "Red • Blue • Yellow • Red • Blue • ?", "opts": ["Red", "Blue", "Yellow", "Green"], "ans": "Yellow"},
        {"p": "Morning • Noon • Evening • Morning • Noon • ?", "opts": ["Morning", "Noon", "Evening", "Night"], "ans": "Evening"},
        {"p": "Spring • Summer • Autumn • Winter • Spring • ?", "opts": ["Spring", "Summer", "Autumn", "Winter"], "ans": "Summer"},
        {"p": "2 • 4 • 6 • 8 • 10 • ?", "opts": ["11", "12", "14", "16"], "ans": "12"},
        {"p": "Circle • Circle • Square • Circle • Circle • ?", "opts": ["Circle", "Square", "Triangle", "Diamond"], "ans": "Square"},
    ],
    3: [
        {"p": "3 • 6 • 9 • 12 • 15 • ?", "opts": ["16", "17", "18", "21"], "ans": "18"},
        {"p": "Red • Green • Green • Red • Green • Green • Red • ?", "opts": ["Red", "Green", "Blue", "Yellow"], "ans": "Green"},
        {"p": "1 • 2 • 4 • 7 • 11 • ?", "opts": ["14", "15", "16", "18"], "ans": "16"},
        {"p": "North • East • South • West • North • ?", "opts": ["North", "East", "South", "West"], "ans": "East"},
        {"p": "A • C • E • G • I • ?", "opts": ["J", "K", "L", "M"], "ans": "K"},
    ],
}

diff_level = state["difficulty_level"] if state["difficulty_level"] in PATTERNS_BY_LEVEL else 1
patterns = PATTERNS_BY_LEVEL[diff_level]


def reset_pm():
    if "pm_state" in st.session_state:
        del st.session_state.pm_state
    st.rerun()


if not state["game_over"]:
    q = patterns[state["q_index"]]

    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 36px 24px; margin-bottom: 24px;">
            <span class="badge badge-blue" style="margin-bottom: 12px;">Question {state['q_index'] + 1} of {len(patterns)}</span>
            <h2 style="font-size: 28px; color: #172536; margin: 12px 0 0 0; line-height: 1.5;">{q['p']}</h2>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, opt in enumerate(q["opts"]):
        with cols[i]:
            if st.button(opt, key=f"pm_opt_{i}", use_container_width=True, type="primary"):
                if opt == q["ans"]:
                    state["correct"] += 1

                state["q_index"] += 1
                if state["q_index"] >= len(patterns):
                    state["game_over"] = True
                st.rerun()

else:
    time_taken = time.time() - state["start_time"]
    score = int((state["correct"] / len(patterns)) * 100)

    if "saved" not in state:
        api.save_game_result(user_id, "Pattern Match", score, score, time_taken, state["difficulty_level"])
        state["saved"] = True

    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 36px; max-width: 600px; margin: 0 auto 24px auto;">
            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 48px; margin-bottom: 8px;">check_circle</span>
            <h2 style="color: #172536; font-size: 1.8rem; margin: 0 0 8px 0;">Session Complete</h2>
            <p style="color: #6B7680; margin-bottom: 20px;">Well done! You worked through all sequence challenges.</p>
            
            <div style="display: flex; justify-content: space-around; background: #F5F7F8; padding: 16px; border-radius: 12px; margin-bottom: 24px;">
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Score</div>
                    <div style="color: #1FA77A; font-size: 1.6rem; font-weight: 700;">{score}%</div>
                </div>
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Correct Answers</div>
                    <div style="color: #3478D4; font-size: 1.6rem; font-weight: 700;">{state['correct']} / {len(patterns)}</div>
                </div>
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Time</div>
                    <div style="color: #17212B; font-size: 1.6rem; font-weight: 700;">{int(time_taken)}s</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3 Working Conclusion Buttons (Section 13)
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("Play Again", key="pm_play_again", type="primary", use_container_width=True):
            reset_pm()
    with col_b2:
        if st.button("Back to Games", key="pm_back_games", use_container_width=True):
            st.switch_page("pages/games_menu.py")
    with col_b3:
        if st.button("View Progress", key="pm_view_progress", use_container_width=True):
            st.switch_page("pages/progress.py")

render_footer()
