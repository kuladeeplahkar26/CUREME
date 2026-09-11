import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .. import models

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def _get_gemini_client():
    """Return a Gemini client if API key is available, else None."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_key_here":
        return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={"timeout": 6000})
        return client
    except Exception:
        return None


# ─────────────────────────────────────────────
# 1. MEMORY Q&A
# ─────────────────────────────────────────────

def answer_memory_question(user_id: int, question: str, db: Session) -> dict:
    """
    Answer a question using stored memories.
    Try Gemini first; fall back to local string-match if unavailable.
    """
    memories = db.query(models.Memory).filter(models.Memory.user_id == user_id).all()

    # Local match (always computed — used as fallback and as context for Gemini)
    local_answer = "I don't have information about that. You can ask your caregiver to add it."
    matched_memory = None

    q_lower = question.lower()
    for m in memories:
        if m.person_name.lower() in q_lower or m.relationship.lower() in q_lower:
            matched_memory = m
            local_answer = (
                f"{m.person_name} is your {m.relationship}. {m.information}"
            )
            break

    # Try Gemini
    client = _get_gemini_client()
    if client and memories:
        try:
            memory_context = "\n".join(
                f"- {m.person_name} ({m.relationship}): {m.information}"
                for m in memories
            )
            prompt = (
                "You are a warm, friendly memory assistant for an elderly person. "
                "Answer their question using ONLY the following stored memories. "
                "If the answer is not in the memories, say so gently.\n\n"
                f"Stored Memories:\n{memory_context}\n\n"
                f"User question: {question}\n\n"
                "Give a short, clear, friendly answer in 1-2 sentences."
            )
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return {"answer": response.text.strip(), "source": "gemini"}
        except Exception:
            pass  # Fall through to local answer

    return {"answer": local_answer, "source": "local"}


# ─────────────────────────────────────────────
# 2. GAME RECOMMENDATION
# ─────────────────────────────────────────────

def get_recommendation(user_id: int, db: Session) -> dict:
    """
    Rule-based recommendation; Gemini rephrases if available.
    """
    from datetime import datetime, timedelta

    all_results = (
        db.query(models.GameResult)
        .filter(models.GameResult.user_id == user_id)
        .order_by(models.GameResult.date.desc())
        .limit(30)
        .all()
    )

    three_days_ago = datetime.utcnow() - timedelta(days=3)
    game_names = ["Memory Match", "Picture Recall", "Pattern Match"]

    # Rule 1: Find a game not played in 3+ days
    recently_played = {r.game_name for r in all_results if r.date >= three_days_ago}
    not_played = [g for g in game_names if g not in recently_played]

    # Rule 2: Find game with lowest recent accuracy
    game_accuracies = {}
    for r in all_results:
        if r.game_name not in game_accuracies:
            game_accuracies[r.game_name] = []
        game_accuracies[r.game_name].append(r.accuracy)

    weakest_game = None
    lowest_acc = 101
    for game, accs in game_accuracies.items():
        avg = sum(accs[:5]) / len(accs[:5])
        if avg < lowest_acc:
            lowest_acc = avg
            weakest_game = game

    # Build rule-based message
    if not_played:
        rule_text = f"Try {not_played[0]} today — you haven't played it in a few days!"
    elif weakest_game:
        rule_text = f"Practice {weakest_game} today to strengthen your skills!"
    else:
        rule_text = "Try any game today to keep your mind active!"

    # Try Gemini to rephrase warmly
    client = _get_gemini_client()
    if client:
        try:
            prompt = (
                "Rephrase this game recommendation for an elderly user in a warm, "
                "encouraging, 1-sentence message. Do not change the game name.\n\n"
                f"Original: {rule_text}"
            )
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return {"recommendation": response.text.strip(), "source": "gemini"}
        except Exception:
            pass

    return {"recommendation": rule_text, "source": "local"}


# ─────────────────────────────────────────────
# 3. PERFORMANCE SUMMARY (Caregiver)
# ─────────────────────────────────────────────

def get_performance_summary(user_id: int, db: Session) -> dict:
    """
    Summarise last 7 days of game results for the caregiver.
    Gemini converts to a narrative if available.
    """
    from datetime import datetime, timedelta

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    results = (
        db.query(models.GameResult)
        .filter(
            models.GameResult.user_id == user_id,
            models.GameResult.date >= seven_days_ago,
        )
        .order_by(models.GameResult.date.desc())
        .all()
    )

    if not results:
        local_summary = "No cognitive activity recorded in the last 7 days."
        return {"summary": local_summary, "source": "local"}

    # Build data summary
    game_stats: dict[str, list[float]] = {}
    for r in results:
        game_stats.setdefault(r.game_name, []).append(r.accuracy)

    lines = []
    for game, accs in game_stats.items():
        avg = sum(accs) / len(accs)
        lines.append(f"{game}: {len(accs)} session(s), avg accuracy {avg:.1f}%")

    data_str = "; ".join(lines)
    local_summary = (
        f"Over the last 7 days: {data_str}. "
        f"Total sessions: {len(results)}."
    )

    # Try Gemini for a caregiver-friendly narrative
    client = _get_gemini_client()
    if client:
        try:
            prompt = (
                "Convert this cognitive activity data into a 2-3 sentence, "
                "caregiver-friendly summary. Use neutral language without clinical conclusions.\n\n"
                f"Data: {local_summary}"
            )
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            return {"summary": response.text.strip(), "source": "gemini"}
        except Exception:
            pass

    return {"summary": local_summary, "source": "local"}
