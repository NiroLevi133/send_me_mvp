# /send_me_mvp/backend/app/routers/onboarding.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas import OnboardingResponse, FocusAnswers, UserProfileBase
from app.services.db_service import get_db, get_user_by_id, update_user, save_targets
from app.services.llm_service import process_resume_and_generate_questions
from app.services.external_api import upload_resume_to_gcs # נניח שיש פונקציה כזו

router = APIRouter()

# Dependency לטעינת משתמש קיים
def get_current_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא קיים")
    return user

@router.post("/resume", response_model=OnboardingResponse)
async def upload_resume_and_onboard(
    user_id: str = Form(..., description="ID המשתמש (Auth Token)"), 
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    ה-Endpoint המאוחד: מקבל קו"ח, מפרק עם LLM, יוצר שאלות ושומר פרופיל.
    """
    user = get_current_user(user_id, db)
    
    # 1. אימות וטיפול בקובץ
    if resume_file.content_type not in ["application/pdf"]: # MVP: נתמך רק ב-PDF
         raise HTTPException(status_code=400, detail="פורמט קובץ חייב להיות PDF")

    file_bytes = await resume_file.read()
    
    # 2. שמירת קו"ח ב-GCS (סימולציה)
    # resume_url = upload_resume_to_gcs(file_bytes, f"{user_id}_{resume_file.filename}") 

    # 3. פירוק וגנרציה באמצעות LLM (שדרוג פרטו)
    # נניח שחולץ טקסט גולמי (בפועל, נשתמש בכלי כמו PyPDF2)
    resume_text_raw = file_bytes.decode('utf-8', errors='ignore') 
    
    llm_output = await process_resume_and_generate_questions(resume_text_raw)
    
    # 4. עדכון פרופיל ב-DB
    profile_data = llm_output.profile_data
    updated_user = update_user(db, user, {
        "name": profile_data.name,
        "email": profile_data.email,
        "resume_text": profile_data.experience_summary, 
        "technologies": profile_data.technologies,
        # "resume_url": resume_url # שמירת הנתיב ל-GCS
    })
    
    # 5. החזרת נתונים ושאלות לפרונטאנד
    return OnboardingResponse(
        profile=UserProfileBase.model_validate(updated_user),
        questions=FocusQuestionsResponse(questions=llm_output.questions)
    )

@router.post("/focus-questions")
def save_focus_answers(
    answers_data: FocusAnswers,
    db: Session = Depends(get_db)
):
    """
    שמירת תשובות המשתמש לשאלות המיקוד כ'יעדים' ו'הדגשים' ב-DB.
    """
    user = get_current_user(answers_data.user_id, db)
    
    # 1. שמירת התשובות (נניח שכל תשובה היא 'highlight' או 'target')
    # save_targets(db, user.id, answers_data.answers) 
    
    # 2. סימון האונבורדינג כהושלם
    update_user(db, user, {"onboarding_complete": True})

    return {"message": "Onboarding completed successfully."}