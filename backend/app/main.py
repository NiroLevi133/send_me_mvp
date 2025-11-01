# /send_me_mvp/backend/app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# ייבוא Routers (אנו מניחים שהם ייווצרו בהמשך)
from app.routers import auth, onboarding, chat 
from app.services.db_service import create_tables # ייבוא לצורך אתחול DB

# טעינת משתני סביבה (עבור הרצה לוקאלית עם python-dotenv)
load_dotenv()

# --- אתחול DB ---
# יצירת הטבלאות בפעם הראשונה (אם אינן קיימות)
create_tables() 

# --- יצירת מופע FastAPI ---
app = FastAPI(
    title="Send_Me MVP API",
    description="מערכת חכמה להגשת מועמדות (MVP).",
    version="1.0.0"
)

# --- טעינת Routers ---
# הגדרת ה-Prefix וה-Tags לשמירה על סדר
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding Flow"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat & Submission"])


# --- Endpoint בריאות בסיסי ---
@app.get("/")
def read_root():
    return {"status": "ok", "service": "Send_Me Backend"}


# --- Middleware CORS (חיוני לפיתוח) ---
# מאפשר ל-Frontend (localhost:3000) לתקשר עם ה-Backend (localhost:8000)
from fastapi.middleware.cors import CORSMiddleware

# קורא את ה-URL של ה-Frontend ממשתני סביבה
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    "http://localhost",
    "http://localhost:8000",
    frontend_url, 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # מאפשר כל המתודות
    allow_headers=["*"], # מאפשר כל ה-Headers
)