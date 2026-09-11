from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models


def get_activity_summary(user_id: int, db: Session):
    today = datetime.utcnow().date()
    # Games played today
    results = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id)\
        .filter(func.date(models.GameResult.date) == today)\
        .all()
    
    summary = {}
    if not results:
        return {"overall_accuracy": 0, "games": {}}
    
    total_acc = 0
    game_counts = {}
    for r in results:
        total_acc += r.accuracy
        if r.game_name not in game_counts:
            game_counts[r.game_name] = {"count": 0, "total_acc": 0}
        game_counts[r.game_name]["count"] += 1
        game_counts[r.game_name]["total_acc"] += r.accuracy

    for g in game_counts:
        summary[g] = game_counts[g]["total_acc"] / game_counts[g]["count"]
    
    overall = total_acc / len(results)
    
    return {"overall_accuracy": overall, "games": summary}

def get_trend_data(user_id: int, db: Session):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    results = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id, models.GameResult.date >= thirty_days_ago)\
        .order_by(models.GameResult.date.asc())\
        .all()
    
    # Format for plotting
    data = []
    for r in results:
        data.append({
            "date": r.date.strftime("%Y-%m-%d"),
            "game_name": r.game_name,
            "accuracy": r.accuracy,
            "score": r.score
        })
    return data

def get_reminder_completion_rate(user_id: int, db: Session):
    total = db.query(models.Reminder).filter(models.Reminder.user_id == user_id).count()
    if total == 0:
        return 0
    completed = db.query(models.Reminder).filter(models.Reminder.user_id == user_id, models.Reminder.status == "completed").count()
    return (completed / total) * 100

def get_activity_flags(user_id: int, db: Session):
    flags = []
    
    # 1. Low activity flag
    five_days_ago = datetime.utcnow() - timedelta(days=5)
    recent_game = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id, models.GameResult.date >= five_days_ago)\
        .first()
    
    if not recent_game:
        flags.append({
            "flag": "Low activity",
            "evidence": "No recorded cognitive activity for 5 days.",
            "suggestion": "Check in with the user."
        })
        
    # 2. Performance change flag
    recent_results = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id)\
        .order_by(models.GameResult.date.desc())\
        .limit(10)\
        .all()
    
    if len(recent_results) >= 5:
        last_3 = sum(r.accuracy for r in recent_results[:3]) / 3
        prev_7 = sum(r.accuracy for r in recent_results[3:]) / len(recent_results[3:])
        if last_3 < prev_7 - 20: # 20% drop
            flags.append({
                "flag": "Performance change",
                "evidence": f"Recent accuracy ({last_3:.1f}%) is below the user's recent baseline ({prev_7:.1f}%).",
                "suggestion": "Observe next sessions or adjust environment."
            })
            
    return flags


def get_comprehensive_patient_analytics(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user_name = user.name if user else "Participant"
    user_age = user.age if user else 70

    games = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id)\
        .order_by(models.GameResult.date.desc())\
        .all()
    
    reminders = db.query(models.Reminder).filter(models.Reminder.user_id == user_id).all()
    completed_reminders = [r for r in reminders if r.status == "completed"]

    # 1. Activities Completed
    activities_completed = len(games) + len(completed_reminders)
    activities_target = 15
    if activities_completed == 0:
        activities_pct = 0
        activities_badge = "Starting fresh (0%)"
        activities_label = "0 / 15 weekly"
        activities_bar_width = 0
    else:
        activities_pct = round((activities_completed / activities_target) * 100)
        activities_badge = f"{activities_pct}% of target" if activities_pct < 100 else f"Goal Achieved ({activities_pct}%)"
        activities_label = f"{activities_completed} / {activities_target} weekly"
        activities_bar_width = min(100, activities_pct)

    # 2. Average Recall Score
    if len(games) == 0:
        avg_recall_score = 0.0
        avg_recall_label = "0%"
        avg_recall_pill = "No sessions yet"
        avg_recall_bar_width = 0
    else:
        avg_recall_score = round(sum(g.accuracy for g in games) / len(games), 1)
        avg_recall_label = f"{int(round(avg_recall_score))}%"
        avg_recall_pill = f"Across {len(games)} session{'s' if len(games) > 1 else ''}"
        avg_recall_bar_width = min(100, int(round(avg_recall_score)))

    # 3. Current Streak
    today = datetime.utcnow().date()
    activity_dates = set()
    for g in games:
        d = g.date.date() if hasattr(g.date, "date") else g.date
        activity_dates.add(d)
    
    streak = 0
    check_date = today
    if check_date not in activity_dates:
        check_date = today - timedelta(days=1)
    while check_date in activity_dates:
        streak += 1
        check_date -= timedelta(days=1)

    if streak == 0:
        streak_label = "0 Days"
        streak_pill = "Start your streak today"
        streak_bar_width = 0
    else:
        streak_label = f"{streak} Day{'s' if streak > 1 else ''}"
        streak_pill = "Consistent Routine"
        streak_bar_width = min(100, round((streak / 7) * 100))

    # 4. Last Interaction
    if len(games) == 0 and len(completed_reminders) == 0:
        last_interaction_title = "No interactions yet"
        last_interaction_detail = "Play a game or complete a routine to begin"
        last_interaction_bar_width = 0
        has_interaction = False
    else:
        has_interaction = True
        if games:
            latest_game = games[0]
            d = latest_game.date
            date_label = "Today" if (hasattr(d, "date") and d.date() == today) else d.strftime("%b %d")
            time_label = d.strftime("%I:%M %p")
            last_interaction_title = f"{date_label}, {time_label}"
            last_interaction_detail = f"{latest_game.game_name} (Score: {int(latest_game.score)}/100)"
            last_interaction_bar_width = 100
        else:
            last_interaction_title = "Routine Checked"
            last_interaction_detail = completed_reminders[0].task
            last_interaction_bar_width = 100

    # 5. Weekly Trends by Category
    def calc_cat_acc(keywords):
        cat_games = [g for g in games if any(kw.lower() in g.game_name.lower() for kw in keywords)]
        if not cat_games:
            return 0
        return int(round(sum(g.accuracy for g in cat_games) / len(cat_games)))

    trends = {
        "memory": calc_cat_acc(["memory", "recall", "card", "picture"]),
        "attention": calc_cat_acc(["attention", "focus", "pattern", "spatial"]),
        "language": calc_cat_acc(["language", "word", "semantic"]),
        "executive": calc_cat_acc(["executive", "puzzle", "tile", "problem"]),
        "has_data": len(games) > 0,
        "total_games": len(games)
    }

    # 6. Recent Activity Items
    recent_activities = []
    for g in games[:6]:
        d = g.date
        date_str = "Today" if (hasattr(d, "date") and d.date() == today) else d.strftime("%b %d")
        time_str = d.strftime("%I:%M %p")
        recent_activities.append({
            "type": "game",
            "title": f"{g.game_name} (Level {g.difficulty_level})",
            "meta": f"{date_str} • {time_str} • Duration {int(g.completion_time or 45)}s",
            "score": f"Score: {int(g.score)}/100",
            "status": "Verified",
            "icon": "extension"
        })
    for r in completed_reminders[:3]:
        recent_activities.append({
            "type": "reminder",
            "title": r.task,
            "meta": f"Routine • {r.time} • Type: {r.reminder_type.upper()}",
            "score": "Confirmed",
            "status": "Done",
            "icon": "task_alt" if r.reminder_type != "medication" else "medication"
        })

    # 7. Adherence Rate
    total_reminders = len(reminders)
    completed_count = len(completed_reminders)
    adherence_pct = round((completed_count / total_reminders) * 100) if total_reminders > 0 else 0

    # 8. Milestones (for My Progress)
    milestones = []
    if len(games) >= 1:
        milestones.append({
            "name": "First Cognitive Step",
            "desc": "Completed first interactive cognitive training session",
            "status": "Earned",
            "icon": "emoji_events",
            "bg": "#E7F4ED",
            "color": "#176B4D"
        })
    if any(g.accuracy >= 90 for g in games):
        milestones.append({
            "name": "Zero-Hint Recall Champion",
            "desc": "Achieved 90%+ accuracy in a cognitive training game",
            "status": "Earned",
            "icon": "psychology",
            "bg": "#D2E4FC",
            "color": "#1F3042"
        })
    if streak >= 3:
        milestones.append({
            "name": f"{streak}-Day Streak Master",
            "desc": f"Maintained consistent cognitive training for {streak} consecutive days",
            "status": "Active",
            "icon": "local_fire_department",
            "bg": "#FFDDB6",
            "color": "#643F00"
        })

    # 9. Vitality Score
    vitality_score = avg_recall_score
    vitality_badge = "Optimal Stability" if vitality_score >= 80 else ("Steady Progress" if vitality_score > 0 else "New Profile • No sessions yet")

    return {
        "user_id": user_id,
        "name": user_name,
        "age": user_age,
        "activities_completed": activities_completed,
        "activities_label": activities_label,
        "activities_badge": activities_badge,
        "activities_bar_width": activities_bar_width,
        "avg_recall_score": avg_recall_score,
        "avg_recall_label": avg_recall_label,
        "avg_recall_pill": avg_recall_pill,
        "avg_recall_bar_width": avg_recall_bar_width,
        "streak_days": streak,
        "streak_label": streak_label,
        "streak_pill": streak_pill,
        "streak_bar_width": streak_bar_width,
        "has_interaction": has_interaction,
        "last_interaction_title": last_interaction_title,
        "last_interaction_detail": last_interaction_detail,
        "last_interaction_bar_width": last_interaction_bar_width,
        "trends": trends,
        "recent_activities": recent_activities,
        "adherence_pct": adherence_pct,
        "adherence_label": f"{adherence_pct}% Complete ({completed_count}/{total_reminders})",
        "milestones": milestones,
        "vitality_score": vitality_score,
        "vitality_badge": vitality_badge,
        "vitality_bar_width": min(100, int(round(vitality_score)))
    }
