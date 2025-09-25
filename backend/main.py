from backend.agents.email_fetcher import EmailFetcherAgent
from backend.agents.email_summarizer import EmailSummarizerAgent
from backend.agents.email_categorizer import EmailCategorizerAgent
from backend.agents.reply_generator import ReplyGeneratorAgent
from backend.agents.reminder_setter import ReminderSetterAgent
from backend.agents.chatbot import ChatbotAgent  # New import

class MailManagementSystem:
    def __init__(self):
        print("Initializing Mail Management System...")
        self.fetcher = EmailFetcherAgent()
        self.summarizer = EmailSummarizerAgent()
        self.categorizer = EmailCategorizerAgent()
        self.reply_generator = ReplyGeneratorAgent()
        self.reminder_setter = ReminderSetterAgent()
        self.chatbot = ChatbotAgent()  # New agent
        self.current_emails = []
        print("All agents initialized successfully!")
    
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
    
    # New method for general chatbot (THIS WAS MISSING - NOW ADDED)
    def general_chat(self, message):
        # Provide stats context for local fallbacks in chatbot
        stats = self.fetcher.get_email_stats(self.current_emails) if self.current_emails else {}
        context = stats  # Pass as dict for parsing in chatbot
        return self.chatbot.general_chat(message, context)