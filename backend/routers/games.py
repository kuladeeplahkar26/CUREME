
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..services import game_service

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/results", response_model=schemas.SaveGameResponse)
def save_game_result(result: schemas.GameResultCreate, db: Session = Depends(database.get_db)):
    new_result = models.GameResult(
        user_id=result.user_id,
        game_name=result.game_name,
        score=result.score,
        accuracy=result.accuracy,
        completion_time=result.completion_time,
        difficulty_level=result.difficulty_level
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    
    new_level, explanation = game_service.compute_new_difficulty(result.user_id, result.game_name, db)

    return schemas.SaveGameResponse(
        message="Game result saved successfully",
        new_level=new_level,
        explanation=explanation
    )

@router.get("/results/{user_id}/recent", response_model=list[schemas.GameResultOut])
def get_recent_game_history(user_id: int, db: Session = Depends(database.get_db)):
    results = db.query(models.GameResult).filter(models.GameResult.user_id == user_id).order_by(models.GameResult.date.desc()).limit(10).all()
    return results

@router.get("/results/{user_id}", response_model=list[schemas.GameResultOut])
def get_game_history(user_id: int, db: Session = Depends(database.get_db)):
    results = db.query(models.GameResult).filter(models.GameResult.user_id == user_id).order_by(models.GameResult.date.desc()).all()
    return results

@router.get("/difficulty/{user_id}/{game_name}")
def get_current_difficulty(user_id: int, game_name: str, db: Session = Depends(database.get_db)):
    last_result = db.query(models.GameResult)\
        .filter(models.GameResult.user_id == user_id, models.GameResult.game_name == game_name)\
        .order_by(models.GameResult.date.desc())\
        .first()
    
    current_level = last_result.difficulty_level if last_result else 1
    # Check if there was a recent difficulty change that hasn't been played yet
    last_log = db.query(models.DifficultyLog)\
        .filter(models.DifficultyLog.user_id == user_id, models.DifficultyLog.game_name == game_name)\
        .order_by(models.DifficultyLog.changed_at.desc())\
        .first()
    
    if last_log and last_result and last_log.changed_at >= last_result.date:
        current_level = last_log.new_level
        
    if not last_result and last_log:
        current_level = last_log.new_level

    return {"game_name": game_name, "difficulty_level": current_level}


@router.get("/difficulty-logs/{user_id}", response_model=list[schemas.DifficultyLogOut])
def get_difficulty_logs(
    user_id: int,
    game_name: str | None = Query(default=None),
    db: Session = Depends(database.get_db),
):
    query = db.query(models.DifficultyLog).filter(models.DifficultyLog.user_id == user_id)
    if game_name:
        query = query.filter(models.DifficultyLog.game_name == game_name)
    return query.order_by(models.DifficultyLog.changed_at.desc()).all()
