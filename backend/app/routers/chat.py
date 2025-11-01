# /send_me_mvp/backend/app/routers/chat.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas import IngestInput, JobData, Submission, SubmissionHistory
from app.services.db_service import get_db, get_user_by_id, create_submission, get_submissions_by_user
from app.services.llm_service import generate_custom_paragraph, extract_job_data_with_llm
from app.services.external_api import extract_job_data_from_image, create_email_message, send_email_with_gmail_api

router = APIRouter()

# Dependency לטעינת משתמש קיים
def get_current_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא קיים")
    if not user.onboarding_complete:
        raise HTTPException(status_code=403, detail="יש להשלים את שלב האונבורדינג")
    return user

@router.post("/ingest", response_model=JobData)
async def ingest_job_ad(ingest_data: IngestInput, db: Session = Depends(get_db)):
    """
    קולט מודעת משרה (טקסט או תמונה) ומחלץ נתונים קריטיים באמצעות Vision/LLM.
    """
    # 1. טיפול בקלט (image_url הוא לצרכי פיתוח, במציאות קובץ מועלה)
    if ingest_data.content_type == "text":
        job_ad_text = ingest_data.content
        # 2. LLM: פירוק טקסט ישירות
        job_data = await extract_job_data_with_llm(job_ad_text)
    
    elif ingest_data.content_type == "image_url":
        # 2. Vision API: ביצוע OCR על התמונה (נניח שקודם בוצעה הורדה לקובץ זמני)
        # image_bytes = download_image(ingest_data.content) 
        # job_data = extract_job_data_from_image(image_bytes)
        
        # סימולציה:
        job_data = JobData(job_title="מפתח בכיר", target_email="test@company.com", requirements=["React", "Python", "SQL"])
        
    else:
        raise HTTPException(status_code=400, detail="Content type לא נתמך.")
    
    # 3. יצירת סבמישן בסטטוס 'draft' ב-DB
    create_submission(db, ingest_data.user_id, job_data)
    
    return job_data

@router.post("/generate/paragraph")
async def generate_paragraph(job_data: JobData, user_id: str, db: Session = Depends(get_db)):
    """
    יוצר פסקה מותאמת אישית לראש המייל על בסיס נתוני המשתמש והמשרה.
    """
    user = get_current_user(user_id, db)
    # 1. איסוף נתונים (קו"ח + יעדים) מהמשתמש
    # user_targets = get_user_targets(db, user.id)
    
    # 2. יצירת הפסקה באמצעות LLM (הפרומפט המורכב)
    paragraph = await generate_custom_paragraph(user, job_data)
    
    return {"paragraph": paragraph}

@router.post("/submit/email")
async def submit_email(
    submission_id: str, 
    final_text: str = Form(...),
    user_id: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    שולח את המייל הסופי באמצעות Gmail API.
    """
    user = get_current_user(user_id, db)
    submission = get_submission_by_id(db, submission_id) # נניח שיש פונקציה זו
    
    if not submission:
        raise HTTPException(status_code=404, detail="הגשה לא נמצאה")
        
    # 1. יצירת הודעת המייל
    message_body = f"""
    שלום רב,
    
    {final_text}
    
    מצורפים קורות חיי.
    
    בברכה,
    {user.name}
    """
    
    raw_message = create_email_message(
        sender=user.email, # בפועל, זו כתובת ה-OAuth
        to=submission.target_email,
        subject=f"מועמדות לתפקיד {submission.job_title}",
        message_text=message_body,
        # attachment_file=user.resume_url # צירוף הקו"ח
    )
    
    # 2. שליחה בפועל (דורש OAuth Flow)
    try:
        # send_email_with_gmail_api(service, user.email, raw_message)
        update_submission_status(db, submission_id, "sent")
    except Exception:
        update_submission_status(db, submission_id, "error")
        raise HTTPException(status_code=500, detail="כשל בשליחת המייל דרך Gmail API")
        
    return {"message": "Email submitted successfully."}

@router.get("/submissions", response_model=SubmissionHistory)
def get_submission_history(user_id: str, db: Session = Depends(get_db)):
    """
    מחזיר את היסטוריית ההגשות של המשתמש (CRM).
    """
    submissions = get_submissions_by_user(db, user_id)
    return SubmissionHistory(submissions=submissions)