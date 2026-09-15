import os
import random
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

st.set_page_config(page_title="Memory Match - MEMOAID", layout="wide")
initialize_session_state()
styles.apply_styles()
render_nav()

if "user_id" not in st.session_state:
    st.switch_page("pages/login.py")

user_id = st.session_state.user_id
assets_dir = Path(__file__).resolve().parents[2] / "assets" / "games" / "memory_match"
asset_paths = {
    "tea_cup": assets_dir / "tea_cup.png",
    "bamboo": assets_dir / "bamboo.png",
    "mustard": assets_dir / "mustard.png",
    "lotus": assets_dir / "lotus.png",
}

st.markdown("""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
        <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 32px;">style</span>
        <h1 style="color: #172536; font-size: 2rem; margin: 0;">Memory Match</h1>
    </div>
    <p style="color: #6B7680; font-size: 1.05rem; margin: 0;">
        Pair familiar everyday items to strengthen visual memory. Find all 4 matching pairs.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize Game State
if "mm_state" not in st.session_state:
    cards = ["tea_cup", "tea_cup", "bamboo", "bamboo", "mustard", "mustard", "lotus", "lotus"]
    random.shuffle(cards)
    difficulty_res = api.get_current_difficulty(user_id, "Memory Match")
    st.session_state.mm_state = {
        "cards": cards,
        "difficulty_level": difficulty_res.get("difficulty_level", 1) if "error" not in difficulty_res else 1,
        "revealed": [False] * 8,
        "matched": [False] * 8,
        "selected": [],
        "attempts": 0,
        "start_time": time.time(),
        "game_over": False
    }

state = st.session_state.mm_state


def reset_game():
    if "mm_state" in st.session_state:
        del st.session_state.mm_state
    st.rerun()


def handle_click(idx):
    if state.get("pending_mismatch"):
        m1, m2 = state["pending_mismatch"]
        state["revealed"][m1] = False
        state["revealed"][m2] = False
        state["selected"] = []
        state["pending_mismatch"] = None

    if state["matched"][idx] or idx in state["selected"] or len(state["selected"]) >= 2:
        return

    state["selected"].append(idx)
    state["revealed"][idx] = True

    if len(state["selected"]) == 2:
        state["attempts"] += 1
        idx1, idx2 = state["selected"]
        if state["cards"][idx1] == state["cards"][idx2]:
            state["matched"][idx1] = True
            state["matched"][idx2] = True
            state["selected"] = []
            if all(state["matched"]):
                state["game_over"] = True
        else:
            state["pending_mismatch"] = [idx1, idx2]


if not state["game_over"]:
    cols = st.columns(4)
    for i in range(8):
        with cols[i % 4]:
            if state["revealed"][i] or state["matched"][i]:
                image_path = asset_paths.get(state["cards"][i])
                if image_path and image_path.exists():
                    st.image(str(image_path), use_container_width=True)
                else:
                    st.markdown(f"<div class='card' style='text-align:center; font-size:24px; padding: 36px 12px; color: #1FA77A;'>{state['cards'][i].replace('_', ' ').title()}</div>", unsafe_allow_html=True)
            else:
                if st.button(f"Card {i + 1}", key=f"card_{i}", use_container_width=True):
                    handle_click(i)
                    st.rerun()

    if state.get("pending_mismatch"):
        st.info("Not a match. Tap any card to continue playing!")
else:
    # Game Over / Session Complete Screen (Section 13)
    time_taken = time.time() - state["start_time"]
    attempts = max(1, state["attempts"])
    score = max(50, min(100, int(100 - (attempts - 4) * 6)))
    accuracy = min(100.0, (4 / attempts) * 100)

    # Save result once
    if "saved" not in state:
        api.save_game_result(user_id, "Memory Match", score, accuracy, time_taken, state["difficulty_level"])
        state["saved"] = True

    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 36px; max-width: 600px; margin: 0 auto 24px auto;">
            <span class="material-symbols-outlined" style="color: #1FA77A; font-size: 48px; margin-bottom: 8px;">check_circle</span>
            <h2 style="color: #172536; font-size: 1.8rem; margin: 0 0 8px 0;">Session Complete</h2>
            <p style="color: #6B7680; margin-bottom: 20px;">Great focus! You found all matching pairs.</p>
            
            <div style="display: flex; justify-content: space-around; background: #F5F7F8; padding: 16px; border-radius: 12px; margin-bottom: 24px;">
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Score</div>
                    <div style="color: #1FA77A; font-size: 1.6rem; font-weight: 700;">{score}%</div>
                </div>
                <div>
                    <div style="color: #6B7680; font-size: 0.85rem;">Correct Pairs</div>
                    <div style="color: #3478D4; font-size: 1.6rem; font-weight: 700;">4 / 4</div>
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
        if st.button("Play Again", key="mm_play_again", type="primary", use_container_width=True):
            reset_game()
    with col_b2:
        if st.button("Back to Games", key="mm_back_games", use_container_width=True):
            st.switch_page("pages/games_menu.py")
    with col_b3:
        if st.button("View Progress", key="mm_view_progress", use_container_width=True):
            st.switch_page("pages/progress.py")

render_footer()
