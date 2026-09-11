
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(prefix="/memories", tags=["memories"])

@router.post("/", response_model=schemas.MemoryOut)
def create_memory(memory: schemas.MemoryCreate, db: Session = Depends(database.get_db)):
    new_memory = models.Memory(**memory.model_dump())
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory

@router.get("/{user_id}", response_model=list[schemas.MemoryOut])
def get_user_memories(user_id: int, db: Session = Depends(database.get_db)):
    memories = db.query(models.Memory).filter(models.Memory.user_id == user_id).all()
    return memories

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(database.get_db)):
    memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(memory)
    db.commit()
    return {"message": "Memory deleted"}
