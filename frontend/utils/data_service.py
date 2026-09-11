import streamlit as st
from utils.api_client import api


def initialize_session_state():
    """Centralized initialization of session state with safe defaults."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
    if "text_size" not in st.session_state:
        st.session_state.text_size = "Standard"
    if "contrast" not in st.session_state:
        st.session_state.contrast = "Standard"
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = False
    if "show_notifications" not in st.session_state:
        st.session_state.show_notifications = False
    if "selected_game" not in st.session_state:
        st.session_state.selected_game = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Good morning. Would you like to start today's activity?"}
        ]


def get_summary_stats(user_id: int):
    """
    Fetch live statistics from backend API if available,
    falling back to clean centralized mock data if empty or offline.
    """
    stats = {
        "activities_today": 4,
        "memory_practice": "78%",
        "attention_score": "72%",
        "current_streak": "5 days",
        "streak_sub": "Keep going",
        "memory_sub": "This week's progress",
        "attention_sub": "Recent performance",
        "activities_sub": "Completed today"
    }

    if not user_id:
        return stats

    try:
        summary = api.get_dashboard_summary(user_id)
        if summary and not isinstance(summary, dict) and "error" in summary:
            return stats
            
        if isinstance(summary, dict) and "games" in summary:
            games_dict = summary.get("games", {})
            if games_dict:
                stats["activities_today"] = len(games_dict)
                if "Memory Match" in games_dict:
                    stats["memory_practice"] = f"{int(games_dict['Memory Match'])}%"
                if "Pattern Match" in games_dict:
                    stats["attention_score"] = f"{int(games_dict['Pattern Match'])}%"
                elif summary.get("overall_accuracy"):
                    stats["attention_score"] = f"{int(summary['overall_accuracy'])}%"
    except Exception:
        pass

    return stats


def get_activities_catalog():
    """All 5 cognitive activities with details and valid routes."""
    return [
        {
            "id": "memory_match",
            "name": "Memory Match",
            "description": "Match familiar objects and strengthen visual memory.",
            "difficulty": "Easy",
            "duration": "3 min",
            "icon": "style",
            "color": "#1FA77A",
            "badge_class": "badge-green",
            "route": "pages/game_memory_match.py"
        },
        {
            "id": "pattern_recall",
            "name": "Pattern Recall",
            "description": "Engage with visual sequences to train rhythmic attention.",
            "difficulty": "Medium",
            "duration": "4 min",
            "icon": "grid_view",
            "color": "#3478D4",
            "badge_class": "badge-blue",
            "route": "pages/game_pattern_match.py"
        },
        {
            "id": "remember_object",
            "name": "Remember the Object",
            "description": "Observe warm pictures and gently recall key details.",
            "difficulty": "Easy",
            "duration": "3 min",
            "icon": "image",
            "color": "#F4C542",
            "badge_class": "badge-yellow",
            "route": "pages/game_picture_recall.py"
        },
        {
            "id": "daily_routine",
            "name": "Daily Routine",
            "description": "Reinforce time milestones, medications, and meals.",
            "difficulty": "Easy",
            "duration": "2 min",
            "icon": "schedule",
            "color": "#1FA77A",
            "badge_class": "badge-green",
            "route": "pages/reminders.py"
        },
        {
            "id": "attention_challenge",
            "name": "Attention Challenge",
            "description": "Target and identify matching patterns with calm pacing.",
            "difficulty": "Medium",
            "duration": "3 min",
            "icon": "psychology",
            "color": "#7B61D9",
            "badge_class": "badge-blue",
            "route": "pages/game_pattern_match.py"
        }
    ]


def get_notifications():
    """List of active notifications for the user."""
    return [
        {"title": "Today's Activity Ready", "time": "10 mins ago", "read": False, "icon": "lightbulb"},
        {"title": "Yesterday's Session Complete", "time": "Yesterday", "read": True, "icon": "check_circle"},
        {"title": "Hydration Reminder Scheduled", "time": "2 hours ago", "read": True, "icon": "water_drop"}
    ]


def get_recent_sessions(user_id: int):
    """Retrieve recent session history from API or fallback."""
    if user_id:
        try:
            results = api.get_game_results(user_id)
            if results and isinstance(results, list) and len(results) > 0:
                formatted = []
                for r in results[:6]:
                    formatted.append({
                        "date": r.get("played_at", "Today")[:10] if r.get("played_at") else "Today",
                        "activity": r.get("game_name", "Cognitive Practice"),
                        "score": f"{int(r.get('accuracy_score', 80))}%",
                        "duration": f"{r.get('reaction_time_ms', 1800) // 1000}s"
                    })
                return formatted
        except Exception:
            pass

    # Centralized demo data
    return [
        {"date": "Today, 10:15 AM", "activity": "Memory Match", "score": "85%", "duration": "2m 45s"},
        {"date": "Yesterday, 4:30 PM", "activity": "Pattern Recall", "score": "75%", "duration": "3m 10s"},
        {"date": "10 Sep, 11:00 AM", "activity": "Remember the Object", "score": "90%", "duration": "2m 15s"},
        {"date": "9 Sep, 02:20 PM", "activity": "Daily Routine", "score": "100%", "duration": "1m 50s"}
    ]
