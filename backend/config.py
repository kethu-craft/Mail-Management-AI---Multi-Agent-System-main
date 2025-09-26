import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Email Configuration
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
    
    # Agent Configuration
    MAX_EMAILS = 10
    SUMMARY_LENGTH = 100
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GEMINI_API_KEY:
            print("⚠️  GEMINI_API_KEY not set")
        if not cls.EMAIL_ADDRESS:
            print("⚠️  EMAIL_ADDRESS not set")
        if not cls.EMAIL_PASSWORD:
            print("⚠️  EMAIL_PASSWORD not set")