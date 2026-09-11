from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import database
from ..services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


class MemoryQuestionRequest(BaseModel):
    user_id: int
    question: str


@router.post("/memory-question")
def memory_question(
    request: MemoryQuestionRequest, db: Session = Depends(database.get_db)
):
    """Answer a question using the user's stored memories (Gemini + local fallback)."""
    return ai_service.answer_memory_question(request.user_id, request.question, db)


@router.get("/recommendation/{user_id}")
def get_recommendation(user_id: int, db: Session = Depends(database.get_db)):
    """Return a personalised game recommendation (rule-based + Gemini phrasing)."""
    return ai_service.get_recommendation(user_id, db)


@router.get("/performance-summary/{user_id}")
def get_performance_summary(user_id: int, db: Session = Depends(database.get_db)):
    """Return a 7-day performance summary for the caregiver (local + Gemini narrative)."""
    return ai_service.get_performance_summary(user_id, db)
