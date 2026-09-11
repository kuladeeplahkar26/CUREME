
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(prefix="/users", tags=["users"])

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[schemas.UserOut])
def get_all_elderly_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).filter(models.User.role == "elderly").all()
    return users

@router.get("/role/caregivers", response_model=list[schemas.UserOut])
def get_all_caregivers(db: Session = Depends(database.get_db)):
    caregivers = db.query(models.User).filter(models.User.role == "caregiver").all()
    return caregivers

@router.get("/caregiver/{caregiver_id}/patients", response_model=list[schemas.UserOut])
def get_patients_for_caregiver(caregiver_id: int, db: Session = Depends(database.get_db)):
    caregiver = db.query(models.User).filter(models.User.id == caregiver_id, models.User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    patients = db.query(models.User).filter(models.User.caregiver_id == caregiver_id).all()
    return patients

@router.post("/caregiver/{caregiver_id}/add-patient", response_model=schemas.UserOut)
def add_patient_for_caregiver(caregiver_id: int, patient_in: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    caregiver = db.query(models.User).filter(models.User.id == caregiver_id, models.User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    
    existing = db.query(models.User).filter(models.User.username == patient_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(patient_in.password or "password123")
    new_patient = models.User(
        username=patient_in.username,
        password_hash=hashed,
        name=patient_in.name,
        age=patient_in.age,
        role="elderly",
        caregiver_id=caregiver_id
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Initial friendly welcome reminder
    db.add(models.Reminder(
        user_id=new_patient.id,
        task="Welcome Gentle Morning Stroll",
        reminder_type="activity",
        date="2026-09-11",
        time="08:00 AM",
        status="pending"
    ))
    if patient_in.relationship:
        db.add(models.Memory(
            user_id=new_patient.id,
            person_name=caregiver.name,
            relationship=patient_in.relationship,
            information=f"{caregiver.name} is {new_patient.name}'s dedicated caregiver."
        ))
    db.commit()
    return new_patient

@router.delete("/caregiver/{caregiver_id}/patient/{patient_id}")
def delete_patient_by_caregiver(caregiver_id: int, patient_id: int, db: Session = Depends(database.get_db)):
    caregiver = db.query(models.User).filter(models.User.id == caregiver_id, models.User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    
    patient = db.query(models.User).filter(models.User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Security check: verify patient belongs to this caregiver
    if patient.caregiver_id != caregiver_id:
        raise HTTPException(status_code=403, detail="Unauthorized: You do not have permission to delete this patient")
    
    # Delete related records
    db.query(models.Reminder).filter(models.Reminder.user_id == patient_id).delete()
    db.query(models.Memory).filter(models.Memory.user_id == patient_id).delete()
    db.query(models.GameResult).filter(models.GameResult.user_id == patient_id).delete()
    db.query(models.DifficultyLog).filter(models.DifficultyLog.user_id == patient_id).delete()
    
    db.delete(patient)
    db.commit()
    return {"message": f"Successfully deleted patient '{patient.name}' (ID: {patient_id})", "patient_id": patient_id}

@router.delete("/caregivers/{caregiver_id}")
def delete_caregiver_account(caregiver_id: int, db: Session = Depends(database.get_db)):
    caregiver = db.query(models.User).filter(models.User.id == caregiver_id, models.User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    
    # Safely unlink associated patients so no orphan / broken foreign keys
    assigned_patients = db.query(models.User).filter(models.User.caregiver_id == caregiver_id).all()
    for p in assigned_patients:
        p.caregiver_id = None
    
    # Delete caregiver's own related records if any
    db.query(models.Reminder).filter(models.Reminder.user_id == caregiver_id).delete()
    db.query(models.Memory).filter(models.Memory.user_id == caregiver_id).delete()
    db.query(models.GameResult).filter(models.GameResult.user_id == caregiver_id).delete()
    db.query(models.DifficultyLog).filter(models.DifficultyLog.user_id == caregiver_id).delete()
    
    db.delete(caregiver)
    db.commit()
    return {
        "message": f"Successfully deleted caregiver account '{caregiver.name}'",
        "unlinked_patients_count": len(assigned_patients)
    }

@router.post("/create-patient", response_model=schemas.UserOut)
def create_patient(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(user.password or "password123")
    new_patient = models.User(
        username=user.username,
        password_hash=hashed,
        name=user.name,
        age=user.age or 70,
        role="elderly",
        caregiver_id=user.caregiver_id
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Seed an initial friendly routine task for the new patient
    db.add(models.Reminder(
        user_id=new_patient.id,
        task="Welcome Gentle Morning Walk",
        reminder_type="activity",
        date="2026-09-11",
        time="08:00 AM",
        status="pending"
    ))
    db.commit()

    return new_patient

@router.post("/create-caregiver", response_model=schemas.UserOut)
def create_caregiver(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(user.password or "password123")
    new_caregiver = models.User(
        username=user.username,
        password_hash=hashed,
        name=user.name,
        age=user.age or 40,
        role="caregiver"
    )
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)
    return new_caregiver

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If caregiver being deleted, unassign their patients
    if user.role == "caregiver":
        assigned = db.query(models.User).filter(models.User.caregiver_id == user_id).all()
        for p in assigned:
            p.caregiver_id = None
    
    # Delete related records
    db.query(models.Reminder).filter(models.Reminder.user_id == user_id).delete()
    db.query(models.Memory).filter(models.Memory.user_id == user_id).delete()
    db.query(models.GameResult).filter(models.GameResult.user_id == user_id).delete()
    db.query(models.DifficultyLog).filter(models.DifficultyLog.user_id == user_id).delete()
    
    db.delete(user)
    db.commit()
    return {"message": f"Successfully deleted user '{user.name}' (ID: {user_id})"}

@router.post("/assign-patient")
def assign_patient_to_caregiver(patient_id: int, caregiver_id: int, db: Session = Depends(database.get_db)):
    patient = db.query(models.User).filter(models.User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    caregiver = db.query(models.User).filter(models.User.id == caregiver_id, models.User.role == "caregiver").first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    patient.caregiver_id = caregiver_id
    db.commit()
    return {"message": f"Assigned patient {patient.name} to caregiver {caregiver.name}"}
