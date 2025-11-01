# /send_me_mvp/backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# טעינת משתני סביבה
load_dotenv()

# ייבוא Routers - נעשה אותם אופציונליים כרגע למקרה שהם לא קיימים
try:
    from app.routers import auth, onboarding, chat 
    from app.services.db_service import create_tables
    routers_available = True
except ImportError:
    routers_available = False
    print("Warning: Routers not found, running in minimal mode")

# --- יצירת מופע FastAPI ---
app = FastAPI(
    title="Send_Me MVP API",
    description="מערכת חכמה להגשת מועמדות (MVP).",
    version="1.0.0",
    docs_url="/api/docs",  # הגדרת נתיב מותאם אישית ל-Swagger
    redoc_url="/api/redoc"
)

# --- Middleware CORS - חשוב מאוד! ---
# מאפשר לכל הדומיינים לגשת (בייצור כדאי להגביל)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בייצור החלף עם הדומיין הספציפי של ה-Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- אתחול DB ---
if routers_available:
    try:
        create_tables()
        print("Database tables created/verified")
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")

# --- טעינת Routers ---
if routers_available:
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding Flow"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat & Submission"])

# --- Health Check Endpoints ---
@app.get("/")
def health_check():
    """בדיקת בריאות בסיסית"""
    return {
        "status": "healthy",
        "service": "Send_Me Backend",
        "version": "1.0.0",
        "message": "Backend is running on Cloud Run!"
    }

@app.get("/api")
def api_root():
    """נקודת כניסה ל-API"""
    return {
        "status": "ok",
        "service": "Send_Me API",
        "endpoints": {
            "health": "/",
            "docs": "/api/docs",
            "auth": "/api/v1/auth",
            "onboarding": "/api/v1/onboarding",
            "chat": "/api/v1/chat"
        }
    }

@app.get("/api/v1")
def api_v1_root():
    """נקודת כניסה ל-API v1"""
    return {
        "version": "1.0",
        "endpoints": [
            "/api/v1/auth",
            "/api/v1/onboarding", 
            "/api/v1/chat"
        ]
    }

# --- Error Handling ---
@app.exception_handler(404)
async def not_found(request, exc):
    return {
        "error": "Not found",
        "message": f"The path {request.url.path} was not found",
        "status": 404
    }

@app.exception_handler(500)
async def server_error(request, exc):
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "status": 500
    }

# הוספת מידע על הפורט שהאפליקציה מאזינה לו
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)