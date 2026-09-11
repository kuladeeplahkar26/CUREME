import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import database
from .routers import ai, auth, games, memories, reminders, users

database.init_db()

app = FastAPI(title="NEUROVIA Cognitive Care Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(memories.router)
app.include_router(reminders.router)
app.include_router(games.router)
app.include_router(ai.router)

# AI router is not included in Phase 1

@app.get("/")
def read_root():
    return {"message": "Welcome to NEUROVIA Cognitive Care Platform API"}

@app.get("/dashboard/summary/{user_id}")
def dashboard_summary(user_id: int, db: database.SessionLocal = Depends(database.get_db)):
    from .services import dashboard_service
    return dashboard_service.get_activity_summary(user_id, db)

@app.get("/dashboard/trends/{user_id}")
def dashboard_trends(user_id: int, db: database.SessionLocal = Depends(database.get_db)):
    from .services import dashboard_service
    return dashboard_service.get_trend_data(user_id, db)

@app.get("/dashboard/flags/{user_id}")
def dashboard_flags(user_id: int, db: database.SessionLocal = Depends(database.get_db)):
    from .services import dashboard_service
    return dashboard_service.get_activity_flags(user_id, db)

@app.get("/dashboard/reminders-rate/{user_id}")
def dashboard_reminders_rate(user_id: int, db: database.SessionLocal = Depends(database.get_db)):
    from .services import dashboard_service
    return {"completion_rate": dashboard_service.get_reminder_completion_rate(user_id, db)}

@app.get("/dashboard/patient-analytics/{user_id}")
def dashboard_patient_analytics(user_id: int, db: database.SessionLocal = Depends(database.get_db)):
    from .services import dashboard_service
    return dashboard_service.get_comprehensive_patient_analytics(user_id, db)

# Mount static web frontend files
web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")
    app.mount("/app", StaticFiles(directory=web_dir, html=True), name="app")
