# /send_me_mvp/backend/app/services/external_api.py
import os
from google.cloud import storage, vision
from typing import List, Dict, Any
from app.schemas import JobData
from email.mime.text import MIMEText
import base64
# import os.path # נדרש ל-Gmail API Auth
# from googleapiclient.discovery import build # נדרש ל-Gmail API

# --- קליינטים ---
GCS_CLIENT = storage.Client()
VISION_CLIENT = vision.ImageAnnotatorClient()

# הגדרת Bucket
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "sendme-resumes-bucket")

# --- 1. שירות GCS ---
def upload_resume_to_gcs(file_bytes: bytes, filename: str, content_type: str) -> str:
    """מעלה קובץ קורות חיים ל-GCS ומחזיר את הנתיב."""
    bucket = GCS_CLIENT.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"resumes/{filename}")
    blob.upload_from_string(file_bytes, content_type=content_type)
    return f"gs://{GCS_BUCKET_NAME}/resumes/{filename}"

# --- 2. שירות Google Vision (OCR) ---
def extract_text_from_image(image_bytes: bytes) -> str:
    """מבצע OCR על תמונת מודעת משרה ומחלץ טקסט גולמי."""
    image = vision.Image(content=image_bytes)
    response = VISION_CLIENT.document_text_detection(image=image)
    return response.full_text_annotation.text

# --- 3. שירות Gmail API (שליחה) ---
def create_email_message(sender: str, to: str, subject: str, message_text: str) -> Dict[str, str]:
    """יוצר אובייקט הודעת מייל מקודד ב-Base64 עבור Gmail API."""
    message = MIMEText(message_text, 'html', 'utf-8')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # ***MVP פשוט: מדלגים על צירוף קובץ כדי להימנע מסיבוכי Multi-Part Message***
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email_with_gmail_api(service, user_email: str, raw_message: Dict[str, str]):
    """שולח את המייל דרך Gmail API (דורש שירות מאומת)."""
    # בפועל, כאן תהיה קריאה ל-service.users().messages().send()
    
    # סימולציה:
    print(f"DEBUG: Email sent from {user_email} to {raw_message.get('to')} successfully!")
    return True