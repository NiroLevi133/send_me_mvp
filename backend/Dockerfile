# Dockerfile מתוקן עבור Backend על Cloud Run
FROM python:3.11-slim

# הגדרות Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# התקנת תלויות
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קוד האפליקציה
COPY . .

# חשוב: Cloud Run דורש שהאפליקציה תקשיב על $PORT
# הוספת gunicorn להרצה על Cloud Run
RUN pip install gunicorn

# הרצה עם gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app -k uvicorn.workers.UvicornWorker
