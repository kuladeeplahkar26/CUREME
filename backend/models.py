# pyrefly: ignore [missing-import]
import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship as db_relationship

from .database import Base


def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    age = Column(Integer)
    role = Column(String) # "elderly" or "caregiver"
    caregiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    caregiver = db_relationship("User", remote_side=[id], backref="assigned_patients")
    memories = db_relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    game_results = db_relationship("GameResult", back_populates="user", cascade="all, delete-orphan")
    reminders = db_relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    difficulty_logs = db_relationship("DifficultyLog", back_populates="user", cascade="all, delete-orphan")

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    person_name = Column(String)
    relationship = Column(String)
    information = Column(String)
    image_url = Column(String, nullable=True)  # base64 data URI or external URL
    created_at = Column(DateTime, default=get_utc_now)

    user = db_relationship("User", back_populates="memories")

class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_name = Column(String)
    score = Column(Float)
    accuracy = Column(Float)
    completion_time = Column(Float)
    difficulty_level = Column(Integer)
    date = Column(DateTime, default=get_utc_now)

    user = db_relationship("User", back_populates="game_results")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task = Column(String)
    reminder_type = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String, default="pending")

    user = db_relationship("User", back_populates="reminders")

class DifficultyLog(Base):
    __tablename__ = "difficulty_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_name = Column(String)
    old_level = Column(Integer)
    new_level = Column(Integer)
    trigger_metric = Column(String)
    trigger_value = Column(Float)
    changed_at = Column(DateTime, default=get_utc_now)
    
    user = db_relationship("User", back_populates="difficulty_logs")
