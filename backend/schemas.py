# pyrefly: ignore [missing-import]
from datetime import datetime

from pydantic import BaseModel, Field


# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    age: int = 70
    role: str = "elderly"
    caregiver_id: int | None = None

class PatientCreate(BaseModel):
    username: str
    password: str | None = "password123"
    name: str
    age: int = 70
    relationship: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    name: str
    age: int | None = None
    role: str
    caregiver_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: int
    username: str
    role: str
    name: str
    assigned_patient_id: int | None = None
    caregiver_id: int | None = None
    message: str = "Authentication successful"

# Memory Schemas
class MemoryCreate(BaseModel):
    user_id: int
    person_name: str
    relationship: str
    information: str
    image_url: str | None = None

class MemoryOut(BaseModel):
    id: int
    user_id: int
    person_name: str
    relationship: str
    information: str
    image_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

# Game Schemas
class GameResultCreate(BaseModel):
    user_id: int
    game_name: str
    score: float = Field(ge=0)
    accuracy: float = Field(ge=0, le=100)
    completion_time: float = Field(ge=0)
    difficulty_level: int = Field(default=1, ge=1, le=3)

class GameResultOut(BaseModel):
    id: int
    user_id: int
    game_name: str
    score: float
    accuracy: float
    completion_time: float
    difficulty_level: int
    date: datetime

    class Config:
        from_attributes = True

class SaveGameResponse(BaseModel):
    message: str
    new_level: int
    explanation: str | None = None

# Reminder Schemas
class ReminderCreate(BaseModel):
    user_id: int
    task: str
    reminder_type: str
    date: str
    time: str

class ReminderOut(BaseModel):
    id: int
    user_id: int
    task: str
    reminder_type: str
    date: str
    time: str
    status: str

    class Config:
        from_attributes = True

class ReminderStatusUpdate(BaseModel):
    status: str

# Difficulty Log Schema
class DifficultyLogOut(BaseModel):
    id: int
    user_id: int
    game_name: str
    old_level: int
    new_level: int
    trigger_metric: str
    trigger_value: float
    changed_at: datetime

    class Config:
        from_attributes = True
