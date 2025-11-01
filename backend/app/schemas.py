# /send_me_mvp/backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- 1. מודלי Auth & Profile ---
class PhoneAuth(BaseModel):
    """קלט עבור כניסת טלפון בלבד."""
    phone_number: str = Field(..., max_length=15)

class UserProfileBase(BaseModel):
    """נתוני פרופיל משתמש בסיסיים."""
    user_id: str
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    onboarding_complete: bool = False

class AuthResponse(BaseModel):
    """תגובה לאחר כניסה/יצירת משתמש."""
    user: UserProfileBase
    is_new_user: bool

# --- 2. מודלי Onboarding (OpenAI Output & Flow) ---
class FocusOption(BaseModel):
    """אופציה לתשובה לשאלה."""
    text: str
    value: str

class FocusQuestion(BaseModel):
    """מבנה שאלה יחידה."""
    q: str
    options: List[FocusOption]

class FocusQuestionsResponse(BaseModel):
    """פלט של OpenAI: רשימת שאלות המיקוד."""
    questions: List[FocusQuestion]

class ResumeAnalysis(BaseModel):
    """נתונים מפורקים מקורות החיים."""
    name: str
    email: str
    experience_summary: str
    technologies: List[str]

class OnboardingCombinedOutput(BaseModel):
    """מבנה משולב מ-LLM (השדרוג): פרופיל מפורק + שאלות."""
    profile_data: ResumeAnalysis
    questions: List[FocusQuestion]

class OnboardingResponse(BaseModel):
    """הפלט הסופי ל-Frontend לאחר העלאת קו"ח."""
    profile: UserProfileBase
    questions: FocusQuestionsResponse
    
class FocusAnswers(BaseModel):
    """קלט לשמירת תשובות המשתמש לשאלות מיקוד."""
    user_id: str
    answers: Dict[str, str] # מפה של Q-ID ל-Value

# --- 3. מודלי Chat & Submission (CRM) ---
class IngestInput(BaseModel):
    """קלט לשליחת מודעת משרה (טקסט/URL תמונה)."""
    user_id: str
    content: str = Field(..., description="טקסט מודעה או URL של תמונה")
    content_type: str = Field(..., description="text או image_url")

class JobData(BaseModel):
    """נתוני משרה שזוהו על ידי OCR/LLM."""
    job_title: str
    target_email: str
    requirements: List[str]

class SubmissionBase(BaseModel):
    """נתוני הגשה בסיסיים."""
    job_title: str
    target_email: str
    submission_text: Optional[str] = None
    job_requirements: Dict[str, Any]

class Submission(SubmissionBase):
    """מודל הגשה מלא (מגיע מה-DB)."""
    submission_id: str
    date_submitted: datetime
    status: str = Field(..., description="draft, sent, error")
    user_id: str

class SubmissionHistory(BaseModel):
    """תגובה עבור מסך ההיסטוריה."""
    submissions: List[Submission]