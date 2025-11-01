# /send_me_mvp/backend/app/services/llm_service.py
import json
import os
from google import genai
from google.genai import types
from app.schemas import OnboardingCombinedOutput, JobData
from typing import Dict, Any, List

# Gemini API Key יקרא ממשתנה הסביבה GEMINI_API_KEY
# חובה להגדיר משתנה סביבה זה ב-Cloud Run
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
MODEL_NAME = "gemini-2.5-flash"

# --- אתחול Gemini Client ---
# ה-Client מוצא אוטומטית את המפתח ממשתנה הסביבה GEMINI_API_KEY
try:
    CLIENT = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    # טיפול באתחול אם המפתח חסר (בפיתוח מקומי ללא מפתח)
    print(f"Gemini Client initialization error: {e}")
    CLIENT = None # נגדיר ל-None כדי למנוע קריסה מיידית


# --- פרומפט 1: פירוק קו"ח ויצירת שאלות ---
def create_onboarding_prompt(resume_text: str) -> str:
    """יוצר פרומפט ל-Gemini לפירוק קורות חיים וגנרציה של שאלות בפורמט JSON."""
    
    return f"""
    אתה מומחה גיוס המנתח קורות חיים.
    המטרה: 
    1. לחלץ נתונים קריטיים על המועמד: שם, מייל, סיכום ניסיון (2-3 משפטים) ורשימת טכנולוגיות מרכזיות (מערך).
    2. לייצר 4-5 שאלות מיקוד (Focus Questions) מותאמות אישית, שמטרתן לחלץ "הדגשים" (Highlights) שניתן לשלב במייל הגשת מועמדות. לכל שאלה, הצע 3-4 תשובות אפשריות.

    הקפד להחזיר רק JSON תקין (Raw JSON) לפי הסכימה הבאה:
    {{
        "profile_data": {{
            "name": "שם המועמד",
            "email": "אימייל",
            "experience_summary": "סיכום ניסיון",
            "technologies": ["טכנולוגיה 1", "טכנולוגיה 2"]
        }},
        "questions": [
            {{
                "q": "השאלה הממוקדת",
                "options": [
                    {{"text": "הסבר אופציה 1", "value": "הדגש שיש לשלב במייל (קצר)"}},
                    {{"text": "הסבר אופציה 2", "value": "הדגש שיש לשלב במייל (קצר)"}}
                ]
            }}
            // ... שאר השאלות
        ]
    }}

    ---
    קורות חיים גולמיים:
    {resume_text}
    ---
    """

async def process_resume_and_generate_questions(resume_text: str) -> OnboardingCombinedOutput:
    if not CLIENT:
        return OnboardingCombinedOutput(profile_data={"name": "חסר", "email": "error@sendme.com", "experience_summary": "שגיאה: חסר GEMINI_API_KEY", "technologies": []}, questions=[])
        
    prompt = create_onboarding_prompt(resume_text)
    
    try:
        response = CLIENT.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", # דורש שהפלט יהיה JSON תקין
            ),
        )
        
        # Gemini מחזיר את ה-JSON כ-response.text
        json_data = json.loads(response.text)
        return OnboardingCombinedOutput(**json_data)
        
    except Exception as e:
        print(f"Error calling Gemini for resume processing: {e}")
        return OnboardingCombinedOutput(profile_data={"name": "שגיאה", "email": "error@sendme.com", "experience_summary": "שגיאת פירוק קו\"ח עקב כשל AI", "technologies": []}, questions=[])


# --- פרומפט 2: יצירת פסקה מותאמת אישית ---
def create_paragraph_prompt(user_data: Dict[str, Any], job_data: JobData) -> str:
    """יוצר פרומפט לכתיבת הפסקה המותאמת אישית."""
    
    highlights_str = "\n- ".join([t['content'] for t in user_data.get('targets', []) if t['type'] == 'highlight'])
    requirements_str = "\n- ".join(job_data.requirements)
    
    return f"""
    אתה כותב קריירה מומחה. כתוב פסקה קצרה (עד 4 משפטים), חזקה ומותאמת אישית לחלוטין, שתשמש כטקסט גוף ראשי במייל הגשת מועמדות.
    
    הפסקה צריכה:
    1. להתמקד ב-2-3 הדרישות העיקריות מהמודעה.
    2. לשלב לפחות אחת מההדגשות המקצועיות ("Highlights") של המועמד.
    3. להיות קולעת, מקצועית וכתובה בעברית רהוטה.
    
    החזר אך ורק את הפסקה המותאמת.

    ---
    ## נתוני קלט:
    - סיכום ניסיון (קו"ח): {user_data.get('resume_text')}
    - טכנולוגיות מפתח: {', '.join(user_data.get('technologies', []))}
    - הדגשים מקצועיים:
    {highlights_str if highlights_str else 'אין הדגשים ספציפיים.'}

    - דרישות המשרה (חובה להתייחס):
    {requirements_str}
    ---
    """

async def generate_custom_paragraph(user_data: Dict[str, Any], job_data: JobData) -> str:
    if not CLIENT:
        return "אנו מתנצלים, אירעה שגיאה: חסר GEMINI_API_KEY."

    prompt = create_paragraph_prompt(user_data, job_data)
    
    try:
        response = CLIENT.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini for paragraph generation: {e}")
        return "אנו מתנצלים, אירעה שגיאה ביצירת הפסקה ע\"י Gemini. אנא נסה שוב."


async def extract_job_data_with_llm(job_ad_text: str) -> JobData:
    """מחלץ נתוני משרה קריטיים מטקסט באמצעות LLM (MVP - דאטא מדומה)."""
    # ... (פונקציה זו נשארה כפי שהיא מהקוד המקורי, מאחר שהפרומפט נשאר דומה)
    # לצורך MVP נחזיר דאטא מדומה:
    return JobData(job_title="מפתח פול-סטאק", target_email="hr@mockcompany.com", requirements=["Python", "FastAPI", "React"])