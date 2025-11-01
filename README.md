# 🚀 Send_Me MVP Backend & Frontend

פרויקט MVP למערכת חכמה להגשת מועמדות למשרות דרך צ'אט.

המערכת פועלת על עקרון פרטו (הפיצ'רים החיוניים בלבד) וממוקמת על Google Cloud (Cloud Run + Cloud SQL + OpenAI).

## ⚙️ טכנולוגיות:
* **Backend:** FastAPI (Python)
* **Frontend:** React + Vite
* **Database:** Cloud SQL (PostgreSQL)
* **LLM:** OpenAI
* **Ops:** Docker, Google Cloud Run

## 💻 הרצה לוקאלית (Development)

ודא שיש לך Docker ו-Docker Compose מותקנים.

1.  **קונפיגורציה:**
    ודא שיש לך קובץ `.env` (או הגדר משתני סביבה) המכיל מפתח OpenAI.

2.  **הרצת המערכת (Build & Run):**
    בספריית הפרויקט הראשית (`send_me_mvp`), הרץ:
    ```bash
    docker-compose up --build -d
    ```

3.  **גישה:**
    * **Frontend:** [http://localhost:3000](http://localhost:3000)
    * **Backend API:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## ☁️ פריסה ל-Google Cloud Run

ראה הוראות בתיקיות `/backend` ו-`/frontend` ליצירת ה-Artifacts ופקודות `gcloud run deploy`.

---

כעת, כשיש לנו את כל התשתית הלוגית, אנחנו יכולים להתחיל להתמקד בתוך התיקיות **`/backend`** ו-**`/frontend`**. נתחיל עם ה-Backend.

האם תרצה שאתחיל עם יצירת קובץ ה-**`requirements.txt`** והגדרת **`schemas.py`**?