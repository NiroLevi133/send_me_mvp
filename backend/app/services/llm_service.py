# /send_me_mvp/backend/app/services/llm_service.py
import json
import os
from openai import OpenAI
from app.schemas import OnboardingCombinedOutput, JobData
from typing import Dict, Any, List

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# --- פרומפט 1: פירוק קו"ח ויצירת שאלות (כבר נכתב, משלים כאן את הפונקציה) ---
def create_onboarding_prompt(resume_text: str) -> str:
    # ... (הקוד כבר נכתב בשלב הקודם) ...
    return f"""
    ... (פרומפט LLM לפירוק קו"ח ויצירת שאלות ב-JSON) ...
    """

async def process_resume_and_generate_questions(resume_text: str) -> OnboardingCombinedOutput:
    # ... (הקוד כבר נכתב בשלב הקודם) ...
    prompt = create_onboarding_prompt(resume_text)
    
    try:
        completion = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "אתה מחזיר JSON תקין לפי המבנה שסופק."},
                {"role": "user", "content": prompt}
            ]
        )
        json_data = json.loads(completion.choices[0].message.content)
        return OnboardingCombinedOutput(**json_data)
    except Exception as e:
        # טיפול בשגיאות
        return OnboardingCombinedOutput(profile_data={"name": "שגיאה", "email": "error@sendme.com", "experience_summary": "שגיאת פירוק קו\"ח", "technologies": []}, questions=[])

# --- פרומפט 2: יצירת פסקה מותאמת אישית (השלמה) ---
def create_paragraph_prompt(user_data: Dict[str, Any], job_data: JobData) -> str:
    """יוצר פרומפט לכתיבת הפסקה המותאמת אישית."""
    
    # עיבוד נתונים מה-DB עבור הפרומפט
    highlights_str = "\n- ".join([t['content'] for t in user_data.get('targets', []) if t['type'] == 'highlight'])
    requirements_str = "\n- ".join(job_data.requirements)
    
    return f"""
    אתה כותב קריירה מומחה. כתוב פסקה קצרה (עד 4 משפטים), חזקה ומותאמת אישית לחלוטין, שתשמש כטקסט גוף ראשי במייל הגשת מועמדות.
    
    הפסקה צריכה:
    1. להתמקד ב-2-3 הדרישות העיקריות מהמודעה.
    2. לשלב לפחות אחת מההדגשות המקצועיות ("Highlights") של המועמד.
    3. להיות קולעת, מקצועית וכתובה בעברית רהוטה.

    ---
    ## נתוני קלט:
    - סיכום ניסיון (קו"ח): {user_data.get('resume_text')}
    - טכנולוגיות מפתח: {', '.join(user_data.get('technologies', []))}
    - הדגשים מקצועיים:
    {highlights_str if highlights_str else 'אין הדגשים ספציפיים.'}

    - דרישות המשרה (חובה להתייחס):
    {requirements_str}
    ---
    
    החזר אך ורק את הפסקה המותאמת.
    """

async def generate_custom_paragraph(user_data: Dict[str, Any], job_data: JobData) -> str:
    """שולח את הפרומפט ליצירת פסקה ל-OpenAI."""
    prompt = create_paragraph_prompt(user_data, job_data)
    
    try:
        completion = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "אתה כותב קריירה מומחה. החזר רק את הפסקה."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI for paragraph generation: {e}")
        return "אנו מתנצלים, אירעה שגיאה ביצירת הפסקה. אנא נסה שוב."

async def extract_job_data_with_llm(job_ad_text: str) -> JobData:
    """מחלץ נתוני משרה קריטיים מטקסט באמצעות LLM."""
    # פרומפט LLM לחילוץ JobData יוכנס כאן.
    # לצורך MVP נחזיר דאטא מדומה:
    return JobData(job_title="מפתח פול-סטאק", target_email="hr@mockcompany.com", requirements=["Python", "FastAPI", "React"])