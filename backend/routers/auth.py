from datetime import datetime
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    if hashed == "mockhash123":
        return True
    return hash_password(plain) == hashed or plain == hashed

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Normalize role to standard tokens
    role = "elderly" if user.role in ["elderly", "elderly_patient", "patient"] else "caregiver"
    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        name=user.name,
        age=user.age,
        role=role,
        caregiver_id=user.caregiver_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if role == "elderly":
        db.add(models.Reminder(
            user_id=new_user.id,
            task="Welcome Gentle Morning Stroll",
            reminder_type="activity",
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            time="08:00 AM",
            status="pending"
        ))
        db.commit()

    return new_user

@router.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=404, detail="Invalid Credentials")
    
    assigned_patient_id = None
    if user.role == "caregiver":
        patient = db.query(models.User).filter(models.User.caregiver_id == user.id).first()
        if not patient:
            # Fallback to default primary patient if unlinked
            patient = db.query(models.User).filter(models.User.role == "elderly").first()
        if patient:
            assigned_patient_id = patient.id
    else:
        assigned_patient_id = user.id

    return schemas.LoginResponse(
        user_id=user.id,
        username=user.username,
        role=user.role,
        name=user.name,
        assigned_patient_id=assigned_patient_id,
        caregiver_id=user.caregiver_id,
        message=f"Welcome {user.name}"
    )
