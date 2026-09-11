import os

import requests
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class BackendUnavailableError(Exception):
    pass

class APIClient:
    def _get(self, endpoint):
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise BackendUnavailableError("Unable to connect to the server.")
        except requests.HTTPError as e:
            return {"error": e.response.json().get("detail", str(e))}

    def _post(self, endpoint, data):
        try:
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise BackendUnavailableError("Unable to connect to the server.")
        except requests.HTTPError as e:
            return {"error": e.response.json().get("detail", str(e))}

    def _patch(self, endpoint, data):
        try:
            response = requests.patch(f"{BACKEND_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise BackendUnavailableError("Unable to connect to the server.")
        except requests.HTTPError as e:
            return {"error": e.response.json().get("detail", str(e))}

    def _delete(self, endpoint):
        try:
            response = requests.delete(f"{BACKEND_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise BackendUnavailableError("Unable to connect to the server.")
        except requests.HTTPError as e:
            return {"error": e.response.json().get("detail", str(e))}

    # Auth
    def login(self, username, password):
        return self._post("/auth/login", {"username": username, "password": password})
    
    def register(self, username, password, name, age, role):
        return self._post("/auth/register", {
            "username": username,
            "password": password,
            "name": name,
            "age": age,
            "role": role
        })

    # Users
    def get_user(self, user_id):
        return self._get(f"/users/{user_id}")
    
    def get_all_elderly_users(self):
        return self._get("/users/")

    # Memories
    def get_memories(self, user_id):
        return self._get(f"/memories/{user_id}")
    
    def add_memory(self, user_id, person_name, relationship, information):
        return self._post("/memories/", {
            "user_id": user_id,
            "person_name": person_name,
            "relationship": relationship,
            "information": information
        })
    
    def delete_memory(self, memory_id):
        return self._delete(f"/memories/{memory_id}")

    # Reminders
    def get_reminders(self, user_id):
        return self._get(f"/reminders/{user_id}")
    
    def add_reminder(self, user_id, task, reminder_type, date, time):
        return self._post("/reminders/", {
            "user_id": user_id,
            "task": task,
            "reminder_type": reminder_type,
            "date": date,
            "time": time
        })
    
    def mark_reminder_complete(self, reminder_id):
        return self._patch(f"/reminders/{reminder_id}/complete", {"status": "completed"})

    def delete_reminder(self, reminder_id):
        return self._delete(f"/reminders/{reminder_id}")

    # Games
    def save_game_result(self, user_id, game_name, score, accuracy, completion_time, difficulty_level=1):
        return self._post("/games/results", {
            "user_id": user_id,
            "game_name": game_name,
            "score": score,
            "accuracy": accuracy,
            "completion_time": completion_time,
            "difficulty_level": difficulty_level
        })
    
    def get_game_history(self, user_id):
        return self._get(f"/games/results/{user_id}")

    def get_recent_game_history(self, user_id):
        return self._get(f"/games/results/{user_id}/recent")

    def get_current_difficulty(self, user_id, game_name):
        return self._get(f"/games/difficulty/{user_id}/{game_name}")

    def get_difficulty_logs(self, user_id, game_name=None):
        endpoint = f"/games/difficulty-logs/{user_id}"
        if game_name:
            endpoint += f"?game_name={game_name}"
        return self._get(endpoint)

    # AI
    def ask_memory_question(self, user_id, question):
        return self._post("/ai/memory-question", {
            "user_id": user_id,
            "question": question
        })

    def get_recommendation(self, user_id):
        return self._get(f"/ai/recommendation/{user_id}")

    def get_performance_summary(self, user_id):
        return self._get(f"/ai/performance-summary/{user_id}")

    # Dashboard
    def get_dashboard_summary(self, user_id):
        return self._get(f"/dashboard/summary/{user_id}")

    def get_trend_data(self, user_id):
        return self._get(f"/dashboard/trends/{user_id}")

    def get_activity_flags(self, user_id):
        return self._get(f"/dashboard/flags/{user_id}")

    def get_reminder_completion_rate(self, user_id):
        return self._get(f"/dashboard/reminders-rate/{user_id}")

api = APIClient()
