import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import database
from .routers import ai, auth, games, memories, reminders, users

database.init_db()

app = FastAPI(title="MEMOAID Cognitive Care Platform API")

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

from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/web/")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MEMOAID Cognitive Care Platform API"}

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

# Mount static web frontend files and assets
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
web_dir = os.path.join(base_dir, "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")
    app.mount("/app", StaticFiles(directory=web_dir, html=True), name="app")

assets_dir = os.path.join(base_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
