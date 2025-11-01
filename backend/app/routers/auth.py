# /send_me_mvp/backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import PhoneAuth, AuthResponse, UserProfileBase
from app.services.db_service import get_db, get_user_by_phone, create_new_user
import uuid

router = APIRouter()

@router.post("/phone", response_model=AuthResponse)
def authenticate_by_phone(
    auth_data: PhoneAuth, 
    db: Session = Depends(get_db)
):
    """
    Endpoint כניסה/הרשמה ראשונית באמצעות מספר טלפון.
    אם המשתמש קיים, טוען את הפרופיל. אם לא, יוצר משתמש חדש.
    """
    phone = auth_data.phone_number.replace('-', '').strip()
    
    # 1. בדיקה אם המשתמש קיים
    user = get_user_by_phone(db, phone)
    is_new_user = user is None
    
    if is_new_user:
        # 2. אם לא קיים: יצירת משתמש חדש
        new_user_id = str(uuid.uuid4())
        user = create_new_user(db, new_user_id, phone)
        
    # 3. החזרת נתוני המשתמש
    profile = UserProfileBase(
        user_id=user.id,
        phone_number=user.phone_number,
        name=user.name,
        email=user.email,
        onboarding_complete=user.onboarding_complete
    )
    
    return AuthResponse(user=profile, is_new_user=is_new_user)