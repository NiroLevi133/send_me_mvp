# /send_me_mvp/backend/Dockerfile.backend

# ------------------------------------
# שלב 1: בניית האפליקציה (התקנת תלויות)
# ------------------------------------
FROM python:3.11-slim as builder

# קונפיגורציית פייתון בסיסית
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# העתקת קובץ התלויות והתקנתן
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קוד המקור של האפליקציה
COPY . .

# ------------------------------------
# שלב 2: יצירת תמונת הרצה נקייה (Run Stage)
# ------------------------------------
# שימוש ב-Base Image מותאם ל-FastAPI/Gunicorn להרצה יעילה ב-Cloud Run
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

# העתקת התלויות והקוד משלב ה-Builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# ה-Base Image כבר מכיל את פקודת ההרצה ומקשיב למשתנה הסביבה $PORT (ברירת מחדל 8000).
# Cloud Run יקצה אוטומטית פורט ויפנה אליו.
EXPOSE 8000