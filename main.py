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
# Action words to look for in messages
ACTION_WORDS = [
    "contact", "reach", "call", "message", "text", "email", "phone", "number", "WhatsApp", "details", 
    "connect", "info", "DM", "chat", "hit", "touch", "send", "share", "exchange", "outside", 
    "continue", "discuss", "offline", "number bejo", "contact bejo", "number chayey", "contact chayey", 
    "whatsapp bejo", "whatsapp cahyey", "whatsapp dedo", "send contact", "share contact", 
    "send number", "send phone", "share number", "share whatsapp", "send whatsapp",
    "number dy do", "number share kro", "calling number do",  
    "Send contact", "Send your contact", "Send ur contact", "Send your number", "Send number", 
    "Send ur number", "Share ur number", "Share your number", "Share contact",  
    "Send whatsapp", "Send your whatsapp", "Send ur whatsapp", "Share ur whatsapp", "Share your whatsapp",  
    "Send email", "Send your email", "Send ur email", "Share email", "Share your email" 
]


# Phone number patterns
# Phone number patterns
PHONE_PATTERNS = [
    r"\+?\d[\d\s\-().]{8,14}\d",  # International formats
    r"\b(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})\b",  # US/Canada local formats

    # Case 1: Numbers separated by commas
    r"\b(?:\d{1,4},)+\d{1,4}\b",  # e.g., 030256,27875
    
    # Case 2: Numbers shared with country mentioned without country code, max 5 digits allowed
    r"\b(?:\d{1,5}(?:\s+[a-zA-Z]+)?(?:\s+\d{1,3})?)\b",  # e.g., 355098765 this is Pakistani number

    # Case 3: Numbers with replaced characters (0 -> O, 1 -> I, etc.)
    r"\b(?:[O0EIIS59]+\s*){8,14}\b",  # e.g., O3O2SO9I8OE

    # Case 4: Roman numeral format with replaced characters
    r"\b(?:[0OIVX1]{1,4}\s+){8,14}\b",  # e.g., 0 III 0 II V 0 V VII V IV VIII VI

    # Case 5: Numbers written in separate messages
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|double|triple)\b",  # e.g., split in messages like zero, double3, etc.

    # Case 6: Mixed number with word counting
    r"\b(?:\d(?:zero|one|two|three|four|five|six|seven|eight|nine|double|triple))+\b",  # e.g., 0zero 5five double4...

    # Case 7: Numbers written in words separated by commas
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|double|triple)\s*,\s*(?:zero|one|two|three|four|five|six|seven|eight|nine|double|triple)\b",  # e.g., zero , three , zero , two...
    
    # English numeral word format
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|double)\s+(?:zero|one|two|three|four|five|six|seven|eight|nine)\b",

    # Urdu numeral word format (Roman script)
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|double|sifar|aik|do|teen|chaar|paanch|chay|saat|aath|no)\s+(?:zero|one|two|three|four|five|six|seven|eight|nine|double|sifar|aik|do|teen|chaar|paanch|chay|saat|aath|no)\b",
    
    # Arabic numeral format
    r"\b(?:٠|١|٢|٣|٤|٥|٦|٧|٨|٩)\s+(?:٠|١|٢|٣|٤|٥|٦|٧|٨|٩)\s+(?:٠|١|٢|٣|٤|٥|٦|٧|٨|٩)\b",
    
    # Urdu numeral word format (Arabic script)
    r"\b(?:صفر|ایک|دو|تین|چار|پانچ|چھ|سات|آٹھ|نو)\s+(?:صفر|ایک|دو|تین|چار|پانچ|چھ|سات|آٹھ|نو)\s+(?:صفر|ایک|دو|تین|چار|پانچ|چھ|سات|آٹھ|نو)\b"
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

# Function to remove long words and flag them
def remove_long_words(text: str, limit: int = 16) -> tuple:
    try:
        words = text.split()
        filtered_words = []
        long_word_flagged = False

        for word in words:
            if len(word) > limit:
                filtered_words.append("[ Phone No Removed ]")  # Replace long word with placeholder
                long_word_flagged = True  # Set the flag to True
            else:
                filtered_words.append(word)

        filtered_text = ' '.join(filtered_words)
        
        return filtered_text, long_word_flagged

    except Exception as e:
        logger.error(f"Error in remove_long_words: {e}")
        raise HTTPException(status_code=500, detail="Error processing the text")

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

        # Remove long words
        text, long_word_detected = remove_long_words(text)

        # Check for action words
        action_word_detected = check_for_action_words(request.text)

        # Return the filtered text along with flags indicating detection
        return {
            "Text": text,
            "phoneNo": phone_detected or long_word_detected,
            "emailAddress": email_detected,
            "IsDetected": phone_detected or email_detected or long_word_detected,
            "IsActionWord": action_word_detected,
        }

    except Exception as e:
        logger.error(f"Unexpected error in filter_text: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
