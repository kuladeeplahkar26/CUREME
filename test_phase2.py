from datetime import date
from uuid import uuid4

import requests


BASE_URL = "http://127.0.0.1:8000"


def request(method, path, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", timeout=20, **kwargs)
    assert response.status_code < 400, response.text
    return response.json()


def test_phase2_end_to_end():
    suffix = uuid4().hex[:8]
    caregiver = request(
        "POST",
        "/auth/register",
        json={
            "username": f"caregiver_{suffix}",
            "password": "password123",
            "name": "Caregiver Test",
            "age": 40,
            "role": "caregiver",
        },
    )
    elderly = request(
        "POST",
        "/auth/register",
        json={
            "username": f"elderly_{suffix}",
            "password": "password123",
            "name": "Elderly Test",
            "age": 70,
            "role": "elderly",
        },
    )
    assert caregiver["role"] == "caregiver"
    user_id = elderly["id"]

    login = request(
        "POST",
        "/auth/login",
        json={"username": f"elderly_{suffix}", "password": "password123"},
    )
    assert login["user_id"] == user_id

    memory = request(
        "POST",
        "/memories/",
        json={
            "user_id": user_id,
            "person_name": "Rahul",
            "relationship": "Grandson",
            "information": "visits every Sunday.",
        },
    )
    assert memory["person_name"] == "Rahul"

    answer = request(
        "POST",
        "/ai/memory-question",
        json={"user_id": user_id, "question": "Who is Rahul?"},
    )
    assert answer["source"] in ("gemini", "local")
    assert "grandson" in answer["answer"].lower()

    recommendation = request("GET", f"/ai/recommendation/{user_id}")
    assert recommendation["source"] in ("gemini", "local")
    assert "recommendation" in recommendation

    summary = request("GET", f"/ai/performance-summary/{user_id}")
    assert summary["source"] in ("gemini", "local")
    assert "summary" in summary

    reminder = request(
        "POST",
        "/reminders/",
        json={
            "user_id": user_id,
            "task": "Take Medicine",
            "reminder_type": "Medicine",
            "date": str(date.today()),
            "time": "09:00",
        },
    )
    request("PATCH", f"/reminders/{reminder['id']}/complete", json={"status": "completed"})
    assert request("GET", f"/dashboard/reminders-rate/{user_id}")["completion_rate"] == 100

    for _ in range(3):
        result = request(
            "POST",
            "/games/results",
            json={
                "user_id": user_id,
                "game_name": "Memory Match",
                "score": 100,
                "accuracy": 100,
                "completion_time": 20,
                "difficulty_level": 1,
            },
        )
    assert result["new_level"] == 2
    assert request("GET", f"/games/difficulty/{user_id}/Memory%20Match")["difficulty_level"] == 2

    logs = request("GET", f"/games/difficulty-logs/{user_id}")
    assert logs[0]["new_level"] == 2

    for _ in range(2):
        result = request(
            "POST",
            "/games/results",
            json={
                "user_id": user_id,
                "game_name": "Memory Match",
                "score": 20,
                "accuracy": 20,
                "completion_time": 40,
                "difficulty_level": 2,
            },
        )
    assert result["new_level"] == 1
    assert request("GET", f"/games/difficulty/{user_id}/Memory%20Match")["difficulty_level"] == 1
    assert len(request("GET", f"/games/difficulty-logs/{user_id}")) == 2

    assert request("GET", f"/dashboard/summary/{user_id}")["games"]["Memory Match"] > 0
    assert request("GET", f"/dashboard/trends/{user_id}")