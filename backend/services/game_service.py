from sqlalchemy.orm import Session

from .. import models


def compute_new_difficulty(user_id: int, game_name: str, db: Session):
    # Fetch last 3 results for this user and game
    recent_results = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id, models.GameResult.game_name == game_name)\
        .order_by(models.GameResult.date.desc())\
        .limit(3)\
        .all()
    
    # Get current difficulty (default to 1 if no history)
    current_level = 1
    if recent_results:
        current_level = recent_results[0].difficulty_level
        
    if not recent_results:
        return current_level, None
        
    # We need 3 results to increase, but can decrease on just 2 bad ones
    recent_accuracies = [r.accuracy for r in recent_results]
    
    new_level = current_level
    explanation = None
    trigger_metric = None
    trigger_value = None

    if len(recent_accuracies) >= 2 and all(acc < 50 for acc in recent_accuracies[:2]):
        if current_level > 1:
            new_level = current_level - 1
            explanation = "We made the next round a little easier based on your recent answers."
            trigger_metric = "low_accuracy"
            trigger_value = sum(recent_accuracies[:2]) / 2
    elif len(recent_accuracies) == 3 and all(acc > 80 for acc in recent_accuracies):
        if current_level < 3:
            new_level = current_level + 1
            explanation = "You're doing great! We made the next round a little more challenging."
            trigger_metric = "high_accuracy"
            trigger_value = sum(recent_accuracies) / 3

    if new_level != current_level:
        log_entry = models.DifficultyLog(
            user_id=user_id,
            game_name=game_name,
            old_level=current_level,
            new_level=new_level,
            trigger_metric=trigger_metric,
            trigger_value=trigger_value
        )
        db.add(log_entry)
        db.commit()

    return new_level, explanation
