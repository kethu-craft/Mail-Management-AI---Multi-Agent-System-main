import datetime
import re
import uuid  # Added for optional UUID-based IDs
from backend.utils.gemini_client import GeminiClient

class ReminderSetterAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.reminders = []
        self.reminder_id_counter = 1
        # Optional: Use UUIDs instead of counter for extra robustness
        self.use_uuid = False  # Toggle to True if you prefer UUIDs
    
    def extract_reminder_info(self, email_content):
        """Extract reminder information from email content using AI"""
        try:
            subject = email_content.get('subject', 'No subject')
            body = email_content.get('body', 'No content')[:1000]
            sender = email_content.get('from', 'Unknown sender')
            
            prompt = f"""
            Analyze this email and determine if it requires any action or follow-up.
            
            Email Subject: {subject}
            From: {sender}
            Content: {body} 
            If this email requires action (like a meeting, task, deadline, or follow-up), 
            respond with:
            ACTION: [clear action description]
            DATE: [specific date if mentioned, otherwise use "TOMORROW"]
            
            If it's just informational (like newsletters, notifications, authentication codes), 
            respond with: NO_ACTION
            
            Examples:
            - "Meeting on Friday" → ACTION: Attend meeting DATE: This Friday
            - "Please review the document" → ACTION: Review document DATE: TOMORROW  
            - "Your verification code is 123456" → NO_ACTION
            - "Newsletter update" → NO_ACTION
            
            Your analysis:
            """
            
            response = self.gemini.generate_text(prompt, max_tokens=150).strip()
            
            if "NO_ACTION" in response.upper():
                return None
            
            # Parse action and date
            action_match = re.search(r'ACTION:\s*(.+)', response, re.IGNORECASE)
            date_match = re.search(r'DATE:\s*(.+)', response, re.IGNORECASE)
            
            if action_match:
                action = action_match.group(1).strip()
                # Clean action text
                action = re.split(r'[\n\r]', action)[0]
                action = re.sub(r'ACTION:?|DATE:?', '', action, flags=re.IGNORECASE).strip()
                
                date = "TOMORROW"
                if date_match:
                    date = date_match.group(1).strip()
                    date = re.sub(r'DATE:?', '', date, flags=re.IGNORECASE).strip()
                
                # Default to tomorrow if no valid date
                if not date or date.upper() in ["ASAP", "SOON"]:
                    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                    date = tomorrow.strftime('%Y-%m-%d')
                
                return {
                    'action': action,
                    'date': date,
                    'email_subject': subject
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting reminder info: {e}")
            return None
    
    def set_reminder(self, email_content, custom_reminder=None):
        """Set a reminder from email content or custom input"""
        try:
            if custom_reminder:
                reminder_info = custom_reminder
            else:
                reminder_info = self.extract_reminder_info(email_content)
                if not reminder_info:
                    return None
            
            # Create reminder
            reminder = {
                'id': str(uuid.uuid4()) if self.use_uuid else self.reminder_id_counter,
                'email_subject': email_content.get('subject', 'No subject'),
                'action': reminder_info.get('action', 'Follow up on email'),
                'date': reminder_info.get('date', 'TOMORROW'),
                'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'completed': False
            }
            
            if not self.use_uuid:
                self.reminder_id_counter += 1
            self.reminders.append(reminder)
            
            # Debug: Log the reminder ID
            print(f"Set reminder with ID: {reminder['id']}")
            
            return reminder
            
        except Exception as e:
            print(f"Error setting reminder: {e}")
            return None
    
    def get_reminders(self):
        """Get all reminders"""
        # Debug: Log all reminder IDs
        print("Current reminder IDs:", [reminder['id'] for reminder in self.reminders])
        return self.reminders
    
    def mark_completed(self, reminder_id):
        """Mark a reminder as completed"""
        try:
            for reminder in self.reminders:
                if reminder['id'] == reminder_id:
                    reminder['completed'] = True
                    reminder['completed_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Marked reminder {reminder_id} as completed")
                    return True
            print(f"Reminder {reminder_id} not found")
            return False
        except Exception as e:
            print(f"Error marking reminder completed: {e}")
            return False
    
    def clear_completed(self):
        """Clear all completed reminders"""
        try:
            initial_count = len(self.reminders)
            self.reminders = [r for r in self.reminders if not r.get('completed', False)]
            cleared_count = initial_count - len(self.reminders)
            print(f"Cleared {cleared_count} completed reminders")
            return cleared_count
        except Exception as e:
            print(f"Error clearing completed reminders: {e}")
            return 0    