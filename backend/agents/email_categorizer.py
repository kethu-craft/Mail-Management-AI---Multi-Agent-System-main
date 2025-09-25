from backend.utils.gemini_client import GeminiClient

class EmailCategorizerAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.categories = ['Work', 'Personal', 'Spam', 'Newsletter', 'Important', 'Social', 'Promotions']
    
    def categorize_email(self, email_subject, email_body, email_from):
        # Clean inputs
        subject = email_subject or "No subject"
        body = str(email_body or "No content")[:1000]
        sender = email_from or "Unknown sender"
        
        prompt = f"""
        Categorize this email into ONE of these categories: {', '.join(self.categories)}. Choose the most fitting one.
        
        FROM: {sender}
        SUBJECT: {subject}
        CONTENT: {body[:500]}  # First 500 chars only
        
        Respond with ONLY the category name. If unsure, default to 'Personal'.
        """
        
        try:
            category = self.gemini.generate_text(prompt, max_tokens=50)
            category = category.strip()
            
            # Validate response
            for valid_cat in self.categories:
                if valid_cat.lower() in category.lower():
                    return valid_cat
            
            # If AI returns invalid category, use fallback
            return self.fallback_categorize(subject, body, sender)
            
        except Exception as e:
            return self.fallback_categorize(subject, body, sender)
    
    def fallback_categorize(self, subject, body, sender):
        """Intelligent fallback categorization"""
        text = f"{subject} {body}".lower()
        sender_lower = sender.lower()
        
        # Keyword-based categorization
        spam_indicators = ['win', 'prize', 'lottery', 'urgent', 'limited', 'congratulations', 'selected']
        work_indicators = ['meeting', 'project', 'deadline', 'report', 'business', 'work', 'office', 'team']
        newsletter_indicators = ['newsletter', 'subscribe', 'unsubscribe', 'digest', 'update']
        social_indicators = ['facebook', 'twitter', 'linkedin', 'instagram', 'invitation', 'friend']
        important_indicators = ['security', 'alert', 'important', 'action required', 'google', 'account']
        promotion_indicators = ['sale', 'discount', 'offer', 'deal', 'promotion', 'buy', 'shop']
        
        if any(indicator in text for indicator in spam_indicators):
            return 'Spam'
        elif any(indicator in text for indicator in work_indicators):
            return 'Work'
        elif any(indicator in text for indicator in newsletter_indicators):
            return 'Newsletter'
        elif any(indicator in text for indicator in social_indicators):
            return 'Social'
        elif any(indicator in text for indicator in important_indicators):
            return 'Important'
        elif any(indicator in text for indicator in promotion_indicators):
            return 'Promotions'
        elif 'google' in sender_lower or 'security' in text:
            return 'Important'
        else:
            return 'Personal'
    
    def categorize_emails(self, emails):
        categorized_emails = []
        for i, email in enumerate(emails):
            category = self.categorize_email(
                email['subject'], 
                email['body'], 
                email['from']
            )
            email['category'] = category
            categorized_emails.append(email)
        
        return categorized_emails
    
    def get_category_stats(self, emails):
        stats = {category: 0 for category in self.categories}
        for email in emails:
            category = email.get('category', 'Personal')
            if category in stats:
                stats[category] += 1
        return stats