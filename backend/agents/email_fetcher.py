from backend.utils.email_client import EmailClient
from backend.config import Config
from datetime import datetime, timedelta

class EmailFetcherAgent:
    def __init__(self):
        self.email_client = EmailClient()
        self.max_emails = Config.MAX_EMAILS
    
    def fetch_recent_emails(self, limit=None):
        if limit is None:
            limit = self.max_emails
        
        emails = self.email_client.fetch_emails(limit=limit)
        return emails
    
    def get_email_stats(self, emails):
        if not emails:
            return {
                'total_emails': 0,
                'unread_count': 0,
                'read_count': 0,
                'today_count': 0,
                'top_senders': {}
            }
        
        total_emails = len(emails)
        unread_count = 0
        read_count = 0
        today_count = 0
        today = datetime.now().date()
        
        senders = {}
        
        for email in emails:
            # Count read/unread
            if email.get('read', False):
                read_count += 1
            else:
                unread_count += 1
            
            # Count emails from today
            try:
                email_date_str = email.get('date', '')
                if email_date_str and email_date_str != 'Unknown Date':
                    email_date = datetime.strptime(email_date_str.split()[0], '%Y-%m-%d').date()
                    if email_date == today:
                        today_count += 1
            except ValueError:
                # Skip invalid dates
                pass
            
            # Count senders
            sender = email.get('from', 'Unknown')
            senders[sender] = senders.get(sender, 0) + 1
        
        # Validate counts (they should add up to total)
        if (unread_count + read_count) != total_emails:
            unread_count = total_emails - read_count
        
        return {
            'total_emails': total_emails,
            'unread_count': unread_count,
            'read_count': read_count,
            'today_count': today_count,
            'top_senders': dict(sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5])
        }