from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import logging

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Home endpoint to check API status
@app.get("/")
def home():
    try:
        return {"status": "API is running successfully!"}
    except Exception as e:
        logger.error(f"Error in home endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error in checking API status")

# Request body model
class TextRequest(BaseModel):
    text: str


# Action words to look for in messages
ACTION_WORDS = [
    "contact", "reach", "call", "message", "text", "email", "phone", "number", "WhatsApp", "details", 
    "connect", "info", "DM", "chat", "hit", "touch", "send", "share", "exchange", "outside", 
    "continue", "discuss", "offline", "number bejo", "contact bejo", "number chayey", "contact chayey", 
    "whatsapp bejo", "whatsapp cahyey", "whatsapp dedo", "send contact", "share contact", 
    "send number", "send phone", "share number", "share whatsapp", "send whatsapp"
]

# Phone number patterns
PHONE_PATTERNS = [
    r"\+?\d[\d\s\-().]{8,14}\d",  # International formats
    r"\b(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})\b",  # US/Canada local formats
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine)\s(?:zero|one|two|three|four|five|six|seven|eight|nine)\s(?:zero|one|two|three|four|five|six|seven|eight|nine)\s(?:zero|one|two|three|four|five|six|seven|eight|nine)\b",  # Word format
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|double|sifar|aik|do|teen|chaar|paanch|chay|saat|aath|no)\s+([zero|one|two|three|four|five|six|seven|eight|nine|double|sifar|aik|do|teen|chaar|paanch|chay|saat|aath|no]\s*){6,9}\b",  # Urdu format
]

# Email patterns
EMAIL_PATTERNS = [
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # Standard email format
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\sdot\scom",  # Email obfuscation format (dot com)
]

# Function to detect and replace sensitive information (phone numbers and emails)
def detect_and_replace(text: str) -> tuple:
    try:
        phone_detected, email_detected = False, False

        # Detect and replace phone numbers
        for pattern in PHONE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                phone_detected = True
                text = re.sub(pattern, "[ Phone No Removed ]", text, flags=re.IGNORECASE)

        # Detect and replace email addresses
        for pattern in EMAIL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                email_detected = True
                text = re.sub(pattern, "[ Email Address Removed ]", text, flags=re.IGNORECASE)

        return text, phone_detected, email_detected

    except Exception as e:
        logger.error(f"Error in detect_and_replace: {e}")
        raise HTTPException(status_code=500, detail="Error detecting and replacing sensitive information")

# Function to check if the message contains any action words
def check_for_action_words(text: str) -> bool:
    try:
        for word in ACTION_WORDS:
            if re.search(rf"\b{word}\b", text, re.IGNORECASE):
                return True
        return False
    except Exception as e:
        logger.error(f"Error in check_for_action_words: {e}")
        raise HTTPException(status_code=500, detail="Error checking for action words")

# Main API endpoint to filter the text
@app.post("/filterText")
def filter_text(request: TextRequest):
    try:
        # Detect and replace phone numbers and emails
        text, phone_detected, email_detected = detect_and_replace(request.text)

        # Check for action words
        action_word_detected = check_for_action_words(request.text)

        # Return the filtered text along with flags indicating detection
        return {
            "Text": text,
            "phoneNo": phone_detected,
            "emailAddress": email_detected,
            "IsDetected": phone_detected or email_detected,
            "IsActionWord": action_word_detected,
        }

    except Exception as e:
        logger.error(f"Unexpected error in filter_text: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
