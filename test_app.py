import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))
from utils.api_client import api


def test_flow():
    print("Testing Registration...")
    res = api.register("john70", "password123", "John Doe", 70, "elderly")
    if "error" in res and "already registered" not in res["error"]:
        print("Registration Error:", res)
        return False
    
    res = api.register("mary_care", "password123", "Caregiver Mary", 40, "caregiver")
    if "error" in res and "already registered" not in res["error"]:
        print("Registration Error (Caregiver):", res)
        return False

    print("Testing Login...")
    res = api.login("john70", "password123")
    if "error" in res:
        print("Login Error:", res)
        return False
    user_id = res["user_id"]
    print("Login successful, user_id:", user_id)

    print("Testing Memories...")
    res = api.add_memory(user_id, "Tommy", "Grandson", "Likes to play football.")
    if "error" in res:
        print("Memory Error:", res)
        return False
    memories = api.get_memories(user_id)
    if not memories:
        print("Failed to get memories")
        return False
    print("Memories successful")

    print("Testing Reminders...")
    res = api.add_reminder(user_id, "Take Meds", "Medicine", "2026-09-11", "08:00")
    if "error" in res:
        print("Reminder Error:", res)
        return False
    reminders = api.get_reminders(user_id)
    if not reminders:
        print("Failed to get reminders")
        return False
    
    api.mark_reminder_complete(reminders[0]["id"])
    print("Reminders successful")

    print("Testing Games...")
    res = api.save_game_result(user_id, "Memory Match", 100, 100, 30)
    if "error" in res:
        print("Game Error:", res)
        return False
    
    difficulty = api.get_current_difficulty(user_id, "Memory Match")
    print("Current Difficulty:", difficulty)

    history = api.get_game_history(user_id)
    if not history:
        print("Failed to get game history")
        return False
    print("Games successful")

    print("Testing Dashboard...")
    summary = api.get_dashboard_summary(user_id)
    print("Summary:", summary)
    
    trends = api.get_trend_data(user_id)
    print("Trends:", len(trends))
    
    flags = api.get_activity_flags(user_id)
    print("Flags:", flags)
    
    rate = api.get_reminder_completion_rate(user_id)
    print("Reminder Rate:", rate)

    print("ALL TESTS PASSED")
    return True

if __name__ == "__main__":
    test_flow()
