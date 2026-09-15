# MEMOAID - Cognitive Wellness Platform

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/kuladeeplahkar26/CUREME)

A compassionate cognitive care platform designed to assist elderly individuals and support caregivers with daily routines, memory exercises, medication reminders, and wellness tracking.

---

## 🚀 1-Click Deploy to Render

Click the button above or visit:
👉 **[Deploy to Render](https://render.com/deploy?repo=https://github.com/kuladeeplahkar26/CUREME)**

Render will automatically detect `render.yaml` and configure the Python web service with:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

---

## 💻 Local Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Custom Data (Optional)
Edit `backend/seed_data.py` with your custom users and run:
```bash
python -m backend.seed_data
```

### 3. Start the Platform
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser at:
- Web Application: [http://localhost:8000/web/](http://localhost:8000/web/)
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📁 Project Architecture
- `backend/`: FastAPI application, SQLite database, routers, and schemas.
- `web/`: Modern responsive web application (HTML5, Vanilla CSS, JS).
- `frontend/`: Streamlit companion dashboard.
- `render.yaml`: Render Blueprint specification.
- `Dockerfile`: Container configuration for universal hosting.
