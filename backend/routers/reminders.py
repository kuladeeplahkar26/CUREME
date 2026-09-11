
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/", response_model=schemas.ReminderOut)
def create_reminder(reminder: schemas.ReminderCreate, db: Session = Depends(database.get_db)):
    new_reminder = models.Reminder(**reminder.model_dump())
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    return new_reminder

@router.get("/{user_id}", response_model=list[schemas.ReminderOut])
def get_user_reminders(user_id: int, db: Session = Depends(database.get_db)):
    reminders = db.query(models.Reminder).filter(models.Reminder.user_id == user_id).all()
    return reminders

@router.patch("/{reminder_id}/complete", response_model=schemas.ReminderOut)
def complete_reminder(reminder_id: int, status_update: schemas.ReminderStatusUpdate, db: Session = Depends(database.get_db)):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.status = status_update.status
    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(database.get_db)):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}
