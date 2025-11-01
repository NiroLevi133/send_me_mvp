# /send_me_mvp/backend/app/services/db_service.py
import os
import uuid
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, JSON, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional, Dict, Any
from app.schemas import UserProfileBase, FocusAnswers

# קריאת משתנה הסביבה (מה-docker-compose או Secret Manager)
# חשוב: עבור Cloud Run, יש להשתמש בחיבור UNIX Socket, אך כאן נשתמש ב-URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/send_me_db") 

# --- הגדרת SQLAlchemy ---
Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

# --- מודלי DB (Mappings) ---

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) # UUID
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
    resume_text = Column(String, nullable=True) # סיכום ניסיון (מה-LLM)
    technologies = Column(JSON, nullable=True) # רשימת טכנולוגיות
    onboarding_complete = Column(Boolean, default=False)
    # resume_url = Column(String, nullable=True) # נתיב GCS

class UserTarget(Base):
    __tablename__ = "user_targets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    type = Column(String) # 'target' (יעד) או 'highlight' (הדגש)
    content = Column(String)
    # ניתן להוסיף 'question_id' כדי לשייך לשאלה המקורית

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(String, index=True)
    date_submitted = Column(DateTime, default=func.now())
    job_title = Column(String)
    target_email = Column(String)
    status = Column(String, default="draft") # draft, sent, error
    submission_text = Column(String, nullable=True)
    job_requirements = Column(JSON, nullable=True)

# --- פונקציות אתחול ו-Dependency Injection ---

def create_tables():
    """יצירת הטבלאות ב-DB (נקרא מ-main.py)."""
    Base.metadata.create_all(bind=Engine)

def get_db():
    """Dependency Injection עבור FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# --- פונקציות CRUD ---

def get_user_by_phone(db_session, phone_number: str) -> Optional[User]:
    return db_session.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_id(db_session, user_id: str) -> Optional[User]:
    return db_session.query(User).filter(User.id == user_id).first()

def create_new_user(db_session, user_id: str, phone_number: str) -> User:
    db_user = User(id=user_id, phone_number=phone_number)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user

def update_user(db_session, user: User, updates: Dict[str, Any]) -> User:
    """עדכון שדות בפרופיל המשתמש."""
    for key, value in updates.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db_session.commit()
    db_session.refresh(user)
    return user

def save_targets(db_session, user_id: str, answers: Dict[str, str]):
    """שמירת תשובות המשתמש לשאלות המיקוד כ-Targets/Highlights."""
    # מחיקת קיימים לפני שמירה
    db_session.query(UserTarget).filter(UserTarget.user_id == user_id).delete()
    
    # סימולציה: נשמור כל תשובה כ-'highlight'
    for q_id, content in answers.items():
        db_target = UserTarget(
            user_id=user_id,
            type='highlight', 
            content=content # בפועל, זהו ה-Value של האופציה
        )
        db_session.add(db_target)
    
    db_session.commit()

def get_user_targets(db_session, user_id: str) -> List[UserTarget]:
    return db_session.query(UserTarget).filter(UserTarget.user_id == user_id).all()
    
def create_submission(db_session, user_id: str, job_data: Dict[str, Any]) -> Submission:
    submission_id = str(uuid.uuid4())
    db_submission = Submission(
        id=submission_id,
        user_id=user_id,
        job_title=job_data.get('job_title', 'לא ידוע'),
        target_email=job_data.get('target_email', 'אין אימייל'),
        job_requirements=job_data.get('requirements', []),
        status="draft"
    )
    db_session.add(db_submission)
    db_session.commit()
    db_session.refresh(db_submission)
    return db_submission

def update_submission_status(db_session, submission_id: str, status: str, text: Optional[str] = None):
    submission = db_session.query(Submission).filter(Submission.id == submission_id).first()
    if submission:
        submission.status = status
        if text:
            submission.submission_text = text
        db_session.commit()
    return submission

def get_submission_by_id(db_session, submission_id: str) -> Optional[Submission]:
    return db_session.query(Submission).filter(Submission.id == submission_id).first()

def get_submissions_by_user(db_session, user_id: str) -> List[Submission]:
    return db_session.query(Submission).filter(Submission.user_id == user_id).order_by(Submission.date_submitted.desc()).all()