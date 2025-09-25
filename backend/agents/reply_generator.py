import datetime
import re
from backend.utils.gemini_client import GeminiClient

class ReplyGeneratorAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.chat_histories = {}
    
    def generate_reply(self, original_email, tone="professional"):
        """Generate a reply for the given email"""
        try:
            subject = original_email.get('subject', 'No subject')
            body = original_email.get('body', 'No content')[:1500]
            sender = original_email.get('from', 'Unknown sender')
            
            valid_tones = ["professional", "casual", "friendly", "formal"]
            if tone not in valid_tones:
                tone = "professional"
            
            prompt = f"""
            Write an email reply based on the following email. 
            Keep it concise (3-5 sentences) and appropriate for the content.
            
            Original Email:
            From: {sender}
            Subject: {subject}
            Content: {body}
            
            Tone: {tone}
            
            Reply Content (start directly with the greeting and message):
            """
            
            response = self.gemini.generate_text(prompt, max_tokens=300)
            
            # Clean the response
            reply = response.strip()
            
            # Remove any quotation marks or unwanted prefixes
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            
            # Ensure it starts properly
            if not reply.startswith(('Dear', 'Hello', 'Hi', 'Thank you', 'Thanks')):
                if tone in ["professional", "formal"]:
                    reply = f"Dear {sender.split()[0] if ' ' in sender else sender},\n\n{reply}"
                else:
                    reply = f"Hello,\n\n{reply}"
            
            return reply
            
        except Exception as e:
            subject = original_email.get('subject', 'this matter')
            return f"""Thank you for your email regarding "{subject}".

I have received your message and will get back to you shortly.

Best regards"""
    
    def chat_with_email(self, email_content, user_message, email_index=0):
        """Chat with AI about a specific email"""
        try:
            subject = email_content.get('subject', 'No subject')
            body = email_content.get('body', 'No content')[:1000]
            sender = email_content.get('from', 'Unknown sender')
            
            # Initialize chat history for this email
            if email_index not in self.chat_histories:
                self.chat_histories[email_index] = []
            
            # Build conversation context
            conversation_context = ""
            for chat in self.chat_histories[email_index][-3:]:  # Last 3 exchanges
                conversation_context += f"Q: {chat.get('user', '')}\nA: {chat.get('assistant', '')}\n\n"
            
            prompt = f"""
            Email Context:
            Subject: {subject}
            From: {sender}
            Content: {body}
            
            Previous Conversation:
            {conversation_context}
            
            New Question: {user_message}
            
            Provide a helpful response based on the email content.
            """
            
            response = self.gemini.generate_text(prompt, max_tokens=250)
            response = response.strip()
            
            # Add to chat history
            chat_entry = {
                'user': user_message,
                'assistant': response,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.chat_histories[email_index].append(chat_entry)
            
            # Keep only last 5 conversations
            if len(self.chat_histories[email_index]) > 5:
                self.chat_histories[email_index] = self.chat_histories[email_index][-5:]
            
            # Convert to streamlit format
            history = []
            for chat in self.chat_histories[email_index]:
                history.append({"role": "user", "content": chat['user']})
                history.append({"role": "assistant", "content": chat['assistant']})
            
            return response, history
            
        except Exception as e:
            error_msg = "I apologize, but I'm having trouble processing your request. Please try again."
            
            # Add error to history
            if email_index not in self.chat_histories:
                self.chat_histories[email_index] = []
            
            chat_entry = {
                'user': user_message,
                'assistant': error_msg,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.chat_histories[email_index].append(chat_entry)
            
            history = []
            for chat in self.chat_histories[email_index]:
                history.append({"role": "user", "content": chat['user']})
                history.append({"role": "assistant", "content": chat['assistant']})
            
            return error_msg, history
    
    def get_chat_history(self, email_index=0):
        """Get chat history for a specific email"""
        return self.chat_histories.get(email_index, [])
    
    def clear_chat_history(self, email_index=0):
        """Clear chat history for a specific email"""
        if email_index in self.chat_histories:
            self.chat_histories[email_index] = []
            return True
        return False