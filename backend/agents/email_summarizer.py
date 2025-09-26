from backend.utils.gemini_client import GeminiClient

class EmailSummarizerAgent:
    def __init__(self):
        self.gemini = GeminiClient()
    
    def summarize_email(self, email_subject, email_body, max_length=100):
        # Clean and prepare email content
        subject = email_subject or "No subject"
        body = str(email_body or "No content")[:1500]  # Limit body length
        
        prompt = f"""
        Summarize this email in no more than {max_length} words:
        
        SUBJECT: {subject}
        
        CONTENT: {body}
        
        Provide a clear, concise summary that captures the main purpose and key points.
        Focus on the most important information.
        """
        
        try:
            summary = self.gemini.generate_text(prompt, max_tokens=150)
            if "unavailable" in summary.lower() or "error" in summary.lower():
                # Fallback summary
                return self.create_fallback_summary(subject, body)
            return summary
        except Exception as e:
            return self.create_fallback_summary(subject, body)
    
    def create_fallback_summary(self, subject, body):
        """Create a basic summary when AI fails"""
        words = body.split()[:30]  # First 30 words for better preview
        preview = " ".join(words)
        return f"Email regarding '{subject}': {preview}..." if preview else "No content available."
    
    def summarize_multiple_emails(self, emails):
        summaries = []
        for i, email in enumerate(emails):
            summary = self.summarize_email(email['subject'], email['body'])
            summaries.append({
                'subject': email['subject'],
                'from': email['from'],
                'summary': summary,
                'date': email['date'],
                'category': email.get('category', 'Unknown')
            })
        return summaries