# pyrefly: ignore [missing-import]
import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.footer import render_footer
from components.nav import render_nav
from utils import styles
from utils.api_client import api
from utils.data_service import initialize_session_state

st.set_page_config(page_title="Remember the Object - NEUROVIA", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id
assets_dir = Path(__file__).resolve().parents[2] / "assets" / "games" / "picture_recall"

st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
        <span class="material-symbols-outlined" style="color: #F4C542; font-size: 32px;">image</span>
        <h1 style="color: #172536; font-size: 2rem; margin: 0;">Remember the Object</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.05rem; margin: 0;">
        Observe the serene setting carefully, then recall details and objects from memory.
    </p>
</div>
""", unsafe_allow_html=True)

if "pr_state" not in st.session_state:
    difficulty_res = api.get_current_difficulty(user_id, "Picture Recall")
    st.session_state.pr_state = {
        "phase": "study",
        "difficulty_level": difficulty_res.get("difficulty_level", 1) if "error" not in difficulty_res else 1,
        "start_time": time.time(),
        "q_index": 0,
        "correct": 0,
        "game_over": False
    }

state = st.session_state.pr_state

QUESTIONS_BY_LEVEL = {
    1: [
        {"q": "What color was the teapot in the picture?", "opts": ["Red", "Blue", "Green", "White"], "ans": "Red"},
        {"q": "How many cups were near the teapot?", "opts": ["Two", "One", "Four", "None"], "ans": "Two"},
        {"q": "Was there a window visible in the background?", "opts": ["Yes", "No"], "ans": "Yes"},
    ],
    2: [
        {"q": "What color was the teapot?", "opts": ["Red", "Blue", "Yellow", "Purple"], "ans": "Red"},
        {"q": "What was the teapot resting on?", "opts": ["A wooden tray", "A glass plate", "A stone counter", "The bare floor"], "ans": "A wooden tray"},
        {"q": "What color was the window frame?", "opts": ["Bright Blue", "Dark Brown", "Deep Green", "White"], "ans": "Bright Blue"},
        {"q": "How many total cups or saucers were shown?", "opts": ["Two", "Three", "One", "Four"], "ans": "Two"},
    ],
    3: [
        {"q": "What shade was the teapot in the scene?", "opts": ["Deep Crimson Red", "Bright Cherry Red", "Burnt Orange", "Muted Pink"], "ans": "Deep Crimson Red"},
        {"q": "On which side of the room was the window located?", "opts": ["Left side", "Right side", "Center top", "Bottom corner"], "ans": "Left side"},
        {"q": "What object was resting on the wooden tray?", "opts": ["The teapot and a cup ring", "Only two cups", "A flower vase", "A tea kettle"], "ans": "The teapot and a cup ring"},
        {"q": "What color was the outer border frame around the scene?", "opts": ["Dark slate navy", "Jet black", "Forest green", "Light gray"], "ans": "Dark slate navy"},
    ],
}

diff_level = state["difficulty_level"] if state["difficulty_level"] in QUESTIONS_BY_LEVEL else 1
questions = QUESTIONS_BY_LEVEL[diff_level]


def reset_pr():
    if "pr_state" in st.session_state:
        del st.session_state.pr_state
    st.rerun()


if state["phase"] == "study":
    st.markdown("""
        <div class="card" style="text-align: center; padding: 24px; margin-bottom: 24px;">
            <h3 style="color: #172536; font-size: 1.25rem; margin-top: 0; margin-bottom: 8px;">Study the Picture</h3>
            <p style="color: #6B7680; margin-bottom: 20px;">Take your time. Notice the colors, objects, and their positions.</p>
    """, unsafe_allow_html=True)

    image_path = assets_dir / f"scene_level_{state['difficulty_level']}.png"
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.markdown("""
            <div style="background-color: #F5F7F8; padding: 40px; border-radius: 12px; margin-bottom: 16px;">
                <span class="material-symbols-outlined" style="font-size: 64px; color: #1FA77A;">coffee</span>
                <p style="color: #17212B; font-size: 1.1rem; font-weight: 500; margin-top: 12px;">
                    A peaceful kitchen counter with a deep crimson red teapot resting on a wooden tray, two matching cups, and a sunlit blue window frame on the left.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn, _ = st.columns([2, 3])
    with col_btn:
        if st.button("I'm Ready to Answer Questions", key="pr_ready_btn", type="primary", use_container_width=True):
            state["phase"] = "quiz"
            st.rerun()

elif state["phase"] == "quiz" and not state["game_over"]:
    q = questions[state["q_index"]]

    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 36px 24px; margin-bottom: 24px;">
            <span class="badge badge-yellow" style="margin-bottom: 12px;">Question {state['q_index'] + 1} of {len(questions)}</span>
            <h2 style="font-size: 26px; color: #172536; margin: 12px 0 0 0; line-height: 1.5;">{q['q']}</h2>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(q["opts"]))
    for i, opt in enumerate(q["opts"]):
        with cols[i]:
            if st.button(opt, key=f"pr_opt_{i}", use_container_width=True, type="primary"):
                if opt == q["ans"]:
                    state["correct"] += 1

                state["q_index"] += 1
                if state["q_index"] >= len(questions):
                    state["game_over"] = True
                st.rerun()

elif state["game_over"]:
    time_taken = time.time() - state["start_time"]
    score = int((state["correct"] / len(questions)) * 100)

    if "saved" not in state:
        api.save_game_result(user_id, "Picture Recall", score, score, time_taken, state["difficulty_level"])
        state["saved"] = True

    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 36px; max-width: 600px; margin: 0 auto 24px auto;">
            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 48px; margin-bottom: 8px;">check_circle</span>
            <h2 style="color: #172536; font-size: 1.8rem; margin: 0 0 8px 0;">Session Complete</h2>
            <p style="color: #6B7680; margin-bottom: 20px;">Great recall! You noted key details with calm accuracy.</p>
            
            <div style="display: flex; justify-content: space-around; background: #F5F7F8; padding: 16px; border-radius: 12px; margin-bottom: 24px;">
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Score</div>
                    <div style="color: #1FA77A; font-size: 1.6rem; font-weight: 700;">{score}%</div>
                </div>
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Correct Answers</div>
                    <div style="color: #3478D4; font-size: 1.6rem; font-weight: 700;">{state['correct']} / {len(questions)}</div>
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
        if st.button("Play Again", key="pr_play_again", type="primary", use_container_width=True):
            reset_pr()
    with col_b2:
        if st.button("Back to Games", key="pr_back_games", use_container_width=True):
            st.switch_page("pages/games_menu.py")
    with col_b3:
        if st.button("View Progress", key="pr_view_progress", use_container_width=True):
            st.switch_page("pages/progress.py")

render_footer()
