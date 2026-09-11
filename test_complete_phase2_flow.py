import os
import sys
from datetime import date, datetime
from uuid import uuid4
import requests

BASE_URL = "http://127.0.0.1:8000"

def req(method, path, **kwargs):
    r = requests.request(method, f"{BASE_URL}{path}", timeout=25, **kwargs)
    assert r.status_code < 400, f"Error {r.status_code}: {r.text}"
    return r.json()

def run_12_step_verification():
    print("\n" + "="*60)
    print("STARTING 12-STEP END-TO-END DEMO FLOW VERIFICATION")
    print("="*60)
    
    unique = uuid4().hex[:6]
    c_user = f"cg_{unique}"
    e_user = f"eld_{unique}"
    
    # Step 1: Caregiver registers & logs in
    print("\n[Step 1] Caregiver registers and logs in...")
    cg_data = req("POST", "/auth/register", json={
        "username": c_user,
        "password": "password123",
        "name": "Dr. Sarah",
        "age": 38,
        "role": "caregiver"
    })
    assert cg_data["role"] == "caregiver"
    cg_login = req("POST", "/auth/login", json={"username": c_user, "password": "password123"})
    assert cg_login["role"] == "caregiver"
    print("  -> Passed: Caregiver registered and authenticated.")

    # Step 2: Creates elderly profile
    print("\n[Step 2] Creating elderly profile...")
    eld_data = req("POST", "/auth/register", json={
        "username": e_user,
        "password": "password123",
        "name": "Grandpa Joe",
        "age": 75,
        "role": "elderly"
    })
    e_id = eld_data["id"]
    assert eld_data["role"] == "elderly"
    all_elderly = req("GET", "/users/")
    assert any(u["id"] == e_id for u in all_elderly)
    print(f"  -> Passed: Elderly profile created (ID: {e_id}, Name: {eld_data['name']}).")

    # Step 3: Adds memory
    print("\n[Step 3] Adding memory: 'Rahul — Grandson — visits every Sunday'...")
    mem_res = req("POST", "/memories/", json={
        "user_id": e_id,
        "person_name": "Rahul",
        "relationship": "Grandson",
        "information": "visits every Sunday."
    })
    assert mem_res["person_name"] == "Rahul"
    mems = req("GET", f"/memories/{e_id}")
    assert any(m["person_name"] == "Rahul" for m in mems)
    print("  -> Passed: Memory recorded in DB.")

    # Step 4: Creates reminder
    print("\n[Step 4] Creating reminder: '09:00 AM — Take Medicine'...")
    rem_res = req("POST", "/reminders/", json={
        "user_id": e_id,
        "task": "Take Medicine",
        "reminder_type": "Medicine",
        "date": str(date.today()),
        "time": "09:00"
    })
    rem_id = rem_res["id"]
    rems = req("GET", f"/reminders/{e_id}")
    assert any(r["id"] == rem_id for r in rems)
    print("  -> Passed: Reminder created and listed.")

    # Step 5: Elderly user logs in
    print("\n[Step 5] Elderly user logs in...")
    eld_login = req("POST", "/auth/login", json={"username": e_user, "password": "password123"})
    assert eld_login["user_id"] == e_id
    assert eld_login["name"] == "Grandpa Joe"
    print("  -> Passed: Elderly user logged in successfully.")

    # Step 6: Plays Memory Match, Picture Recall, Pattern Match
    print("\n[Step 6] Playing cognitive games...")
    # Play Memory Match (score 100)
    g1 = req("POST", "/games/results", json={
        "user_id": e_id,
        "game_name": "Memory Match",
        "score": 100,
        "accuracy": 100,
        "completion_time": 24,
        "difficulty_level": 1
    })
    assert "new_level" in g1
    # Play Picture Recall
    g2 = req("POST", "/games/results", json={
        "user_id": e_id,
        "game_name": "Picture Recall",
        "score": 80,
        "accuracy": 80,
        "completion_time": 35,
        "difficulty_level": 1
    })
    # Play Pattern Match
    g3 = req("POST", "/games/results", json={
        "user_id": e_id,
        "game_name": "Pattern Match",
        "score": 100,
        "accuracy": 100,
        "completion_time": 20,
        "difficulty_level": 1
    })
    print("  -> Passed: All 3 cognitive games executed and results saved.")

    # Step 7: Game ends, score saved, adaptive difficulty verified
    print("\n[Step 7] Testing Adaptive Difficulty Engine...")
    # Add 2 more high score rounds for Memory Match to trigger level up
    req("POST", "/games/results", json={"user_id": e_id, "game_name": "Memory Match", "score": 90, "accuracy": 90, "completion_time": 22, "difficulty_level": 1})
    g_up = req("POST", "/games/results", json={"user_id": e_id, "game_name": "Memory Match", "score": 95, "accuracy": 95, "completion_time": 20, "difficulty_level": 1})
    assert g_up["new_level"] == 2
    cur_diff = req("GET", f"/games/difficulty/{e_id}/Memory%20Match")
    assert cur_diff["difficulty_level"] == 2
    logs = req("GET", f"/games/difficulty-logs/{e_id}")
    assert len(logs) >= 1
    assert logs[0]["new_level"] == 2
    print(f"  -> Passed: Difficulty adapted to Level {cur_diff['difficulty_level']} with log trigger '{logs[0]['trigger_metric']}'.")

    # Step 8: Recommendation shown on dashboard
    print("\n[Step 8] Checking activity recommendation...")
    rec = req("GET", f"/ai/recommendation/{e_id}")
    assert "recommendation" in rec
    assert rec["source"] in ("gemini", "local")
    print(f"  -> Passed: Recommendation [{rec['source']}]: '{rec['recommendation']}'.")

    # Step 9 & 10: Memory Assistant Q&A: 'Who is Rahul?'
    print("\n[Step 9 & 10] Testing Memory Assistant ('Who is Rahul?')...")
    qa = req("POST", "/ai/memory-question", json={"user_id": e_id, "question": "Who is Rahul?"})
    assert "grandson" in qa["answer"].lower()
    assert qa["source"] in ("gemini", "local")
    print(f"  -> Passed: Memory Assistant [{qa['source']}]: '{qa['answer']}'.")

    # Step 11: Complete reminder and verify rate
    print("\n[Step 11] Marking reminder complete and checking caregiver summary...")
    req("PATCH", f"/reminders/{rem_id}/complete", json={"status": "completed"})
    rate = req("GET", f"/dashboard/reminders-rate/{e_id}")
    assert rate["completion_rate"] == 100.0
    summary = req("GET", f"/dashboard/summary/{e_id}")
    assert "Memory Match" in summary["games"]
    assert "Picture Recall" in summary["games"]
    assert "Pattern Match" in summary["games"]
    print(f"  -> Passed: Reminder rate {rate['completion_rate']}%, Summary games: {list(summary['games'].keys())}.")

    # Step 12: Activity trends, caregiver narrative summary, safety flags
    print("\n[Step 12] Checking caregiver activity trends, AI narrative, and safety flags...")
    trends = req("GET", f"/dashboard/trends/{e_id}")
    assert len(trends) >= 5
    perf_summary = req("GET", f"/ai/performance-summary/{e_id}")
    assert "summary" in perf_summary
    assert perf_summary["source"] in ("gemini", "local")
    flags = req("GET", f"/dashboard/flags/{e_id}")
    # Verify no prohibited medical words in flags
    for f in flags:
        assert "decline" not in f["flag"].lower()
        assert "deteriorat" not in f["flag"].lower()
    print(f"  -> Passed: Trends count={len(trends)}, Narrative [{perf_summary['source']}]: '{perf_summary['summary']}'.")
    print(f"  -> Passed: Safety flags={flags} (No medical/prohibited terminology).")

    print("\n" + "="*60)
    print("ALL 12 STEPS PASSED PERFECTLY!")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_12_step_verification()
