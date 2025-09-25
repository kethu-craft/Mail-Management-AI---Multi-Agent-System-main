# [file name]: email_client.py
# [file content begin]
from imap_tools import MailBox, AND
from backend.config import Config
import email
from email.header import decode_header
import datetime

class EmailClient:
    def __init__(self):
        self.email_address = Config.EMAIL_ADDRESS
        self.password = Config.EMAIL_PASSWORD
        self.imap_server = Config.IMAP_SERVER
        self.imap_port = Config.IMAP_PORT
    
    def connect(self):
        try:
            self.mailbox = MailBox(self.imap_server, self.imap_port)
            self.mailbox.login(self.email_address, self.password)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def fetch_emails(self, limit=10, folder='INBOX'):
        if not hasattr(self, 'mailbox'):
            if not self.connect():
                return []
        
        try:
            self.mailbox.folder.set(folder)
            emails = []
            
            # Fetch emails with proper flag detection
            for msg in self.mailbox.fetch(limit=limit, reverse=True, mark_seen=False):
                # DEBUG: Print flags to see what's available
                print(f"Email flags for {msg.subject}: {msg.flags}")
                
                # Different methods to detect read status
                is_read = False
                
                # Method 1: Check for SEEN flag (standard IMAP)
                if 'SEEN' in msg.flags:
                    is_read = True
                # Method 2: Check for \\Seen flag (some servers use this)
                elif '\\Seen' in msg.flags:
                    is_read = True
                # Method 3: Check if message has been answered or forwarded
                elif any(flag in msg.flags for flag in ['ANSWERED', 'FORWARDED']):
                    is_read = True
                
                email_data = {
                    'uid': msg.uid,
                    'subject': msg.subject or "No Subject",
                    'from': msg.from_ or "Unknown Sender",
                    'date': msg.date.strftime('%Y-%m-%d %H:%M:%S') if msg.date else "Unknown Date",
                    'body': msg.text or msg.html or "No content",
                    'read': is_read,
                    'flags': list(msg.flags)  # Keep for debugging
                }
                emails.append(email_data)
                print(f"Email '{msg.subject[:30]}...' - Read: {is_read}, Flags: {msg.flags}")
            
            # Count actual read/unread
            unread_count = sum(1 for e in emails if not e['read'])
            print(f"DEBUG: Fetched {len(emails)} emails, {unread_count} unread")
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def send_email(self, to, subject, body):
        # Note: This is a placeholder. You'd need SMTP setup for sending
        print(f"Would send email to: {to}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        return True
    
    def disconnect(self):
        if hasattr(self, 'mailbox'):
            self.mailbox.logout()
# [file content end]