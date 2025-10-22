# [file name]: main.py
# [file content begin]
from backend.agents.email_fetcher import EmailFetcherAgent
from backend.agents.email_summarizer import EmailSummarizerAgent
from backend.agents.email_categorizer import EmailCategorizerAgent
from backend.agents.reply_generator import ReplyGeneratorAgent
from backend.agents.reminder_setter import ReminderSetterAgent
from backend.agents.chatbot import ChatbotAgent
from backend.auth import AuthSystem
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from backend.config import Config

class MailManagementSystem:
    def __init__(self):
        print("Initializing Mail Management System...")
        self.fetcher = EmailFetcherAgent()
        self.summarizer = EmailSummarizerAgent()
        self.categorizer = EmailCategorizerAgent()
        self.reply_generator = ReplyGeneratorAgent()
        self.reminder_setter = ReminderSetterAgent()
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.chatbot = ChatbotAgent()
        self.current_emails = []
        self.auth_system = AuthSystem()
        print("All agents initialized successfully!")
    
    # NEW: OTP Authentication methods
    def initiate_registration(self, email):
        """Initiate registration by sending OTP"""
        return self.auth_system.initiate_registration(email)
    
    def verify_otp(self, email, otp):
        """Verify OTP for registration"""
        return self.auth_system.verify_otp(email, otp)
    
    def complete_registration(self, email, password):
        """Complete registration after OTP verification"""
        return self.auth_system.complete_registration(email, password)
    
    def resend_otp(self, email):
        """Resend OTP to user"""
        return self.auth_system.resend_otp(email)
    
    def login_user(self, email, password):
        """Authenticate user"""
        return self.auth_system.login_user(email, password)
    
    def verify_token(self, token):
        """Verify JWT token"""
        return self.auth_system.verify_token(token)
    
    def user_exists(self, email):
        """Check if user exists"""
        return self.auth_system.user_exists(email)

    # NEW: Delete account method
    def delete_account(self, email, password):
        """Delete user account"""
        return self.auth_system.delete_account(email, password)
    
    # ... (rest of your existing methods remain the same)
    def fetch_and_process_emails(self, limit=10):
        print(f"Fetching and processing {limit} emails...")
        try:
            # Step 1: Fetch emails
            print("Step 1: Fetching emails...")
            self.current_emails = self.fetcher.fetch_recent_emails(limit)
            print(f"Fetched {len(self.current_emails)} emails")
            
            if not self.current_emails:
                return self.create_empty_response()
            
            # Step 2: Categorize emails
            print("Step 2: Categorizing emails...")
            categorized_emails = self.categorizer.categorize_emails(self.current_emails)
            print("Categorization completed")
            
            # Step 3: Summarize emails
            print("Step 3: Summarizing emails...")
            summarized_emails = self.summarizer.summarize_multiple_emails(categorized_emails)
            print("Summarization completed")
            
            # Step 4: Get statistics
            stats = self.fetcher.get_email_stats(self.current_emails)
            category_stats = self.categorizer.get_category_stats(categorized_emails)
            
            print("Email processing completed successfully!")
            
            return {
                'emails': summarized_emails,
                'stats': stats,
                'category_stats': category_stats,
                'raw_emails': self.current_emails
            }
            
        except Exception as e:
            print(f"Error in fetch_and_process_emails: {e}")
            return self.create_empty_response()
    
    def create_empty_response(self):
        return {
            'emails': [],
            'stats': {'total_emails': 0, 'unread_count': 0, 'top_senders': {}},
            'category_stats': {},
            'raw_emails': []
        }
    
    def generate_reply_for_email(self, email_index, tone="professional"):
        if 0 <= email_index < len(self.current_emails):
            return self.reply_generator.generate_reply(self.current_emails[email_index], tone)
        return "Invalid email index"
    
    def set_reminder_for_email(self, email_index, custom_reminder=None):
        if 0 <= email_index < len(self.current_emails):
            return self.reminder_setter.set_reminder(self.current_emails[email_index], custom_reminder)
        return None
    
    def chat_about_email(self, email_index, message):
        if 0 <= email_index < len(self.current_emails):
            return self.reply_generator.chat_with_email(self.current_emails[email_index], message)
        return "Invalid email index", []
    
    def get_reminders(self):
        return self.reminder_setter.get_reminders()
    
    def mark_reminder_completed(self, reminder_id):
        return self.reminder_setter.mark_completed(reminder_id)
    
    def clear_completed_reminders(self):
        """Clear all completed reminders"""
        return self.reminder_setter.clear_completed()
    
    def general_chat(self, message):
        # Provide stats context for local fallbacks in chatbot
        stats = self.fetcher.get_email_stats(self.current_emails) if self.current_emails else {}
        context = stats  # Pass as dict for parsing in chatbot
        return self.chatbot.general_chat(message, context)
    
    def send_email(self, to_address, subject, body, in_reply_to=None, references=None):
        """
        Send an email using SMTP.
        
        Args:
            to_address (str): Recipient's email address
            subject (str): Email subject
            body (str): Email body content
            in_reply_to (str, optional): Message-ID of the email being replied to
            references (str, optional): References header for threading
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            
            # Add reply headers for threading
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
            if references:
                msg['References'] = references
            
            # Attach the body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server (example for Gmail)
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            # Send the email
            server.sendmail(self.email_address, to_address, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
# [file content end]