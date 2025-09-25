import datetime
from backend.utils.gemini_client import GeminiClient

class ChatbotAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.chat_history = []
    
    def general_chat(self, message, context=""):
        """Handle general chat queries about mail management with local fallbacks"""
        try:
            # Local fallback for common stats queries (no API needed)
            if "unread" in message.lower() or "how many emails" in message.lower():
                # Parse context for stats (passed from main.py)
                total = context.get('total_emails', 0) if isinstance(context, dict) else 0
                unread = context.get('unread_count', 0) if isinstance(context, dict) else 0
                read = total - unread
                fallback_response = f"Based on your recent emails: You have {unread} unread and {read} read out of {total} total. Tip: Prioritize unread by category (e.g., Work/Important)."
                if "tip" in message.lower() or "organizing" in message.lower():
                    fallback_response += "\n\nOrganizing Tips: 1) Use labels/folders for categories. 2) Set auto-rules for newsletters. 3) Unsubscribe from spam sources. 4) Schedule 'inbox zero' time daily."
                print("🔍 Using local fallback for stats query.")
                return fallback_response, [{"role": "user", "content": message}, {"role": "assistant", "content": fallback_response}]
            
            if "tip" in message.lower() or "organize" in message.lower():
                fallback_response = "Email Organizing Tips: 1) Categorize immediately (Work/Personal). 2) Use search for quick finds. 3) Archive/delete weekly. 4) Set reminders for action items. 5) Limit inbox to 50 emails max."
                return fallback_response, [{"role": "user", "content": message}, {"role": "assistant", "content": fallback_response}]
            
            # For other queries, use API with retry handling
            conversation_context = ""
            for chat in self.chat_history[-3:]:  # Last 3 exchanges for context
                conversation_context += f"User: {chat.get('user', '')}\nAssistant: {chat.get('assistant', '')}\n\n"
            
            prompt = f"""
            You are a helpful email management assistant. Answer the user's query concisely and helpfully.
            You can provide advice on email organization, summaries of the mailbox, or general tips.
            
            Mailbox context (if available): {context}
            
            Previous conversation:
            {conversation_context}
            
            User query: {message}
            """
            
            response = self.gemini.generate_text(prompt, max_tokens=300).strip()
            
            # Add to history
            chat_entry = {
                'user': message,
                'assistant': response,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.chat_history.append(chat_entry)
            
            # Keep last 10 entries
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            # Format history for frontend
            history = []
            for chat in self.chat_history:
                history.append({"role": "user", "content": chat['user']})
                history.append({"role": "assistant", "content": chat['assistant']})
            
            return response, history
        
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}. Try a simpler query."
            if "quota" in str(e).lower():
                error_msg = "Quota exceeded—try stats queries (they work offline) or wait 24h."
            self.chat_history.append({
                'user': message,
                'assistant': error_msg,
                'timestamp': datetime.datetime.now().isoformat()
            })
            history = [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}]
            return error_msg, history