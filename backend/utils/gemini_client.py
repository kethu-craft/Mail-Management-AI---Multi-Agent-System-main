import google.generativeai as genai
import time  # For backoff retries
from backend.config import Config

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Use newer model (1.5 retiring Sep 24, 2025)
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            print("✅ Using model: gemini-2.5-flash-lite")  # Debug print
        except Exception as e:
            print(f"⚠️ Failed to load gemini-2.5-flash-lite: {e}")
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fallback to old (if still active)
                print("✅ Using model: gemini-1.5-flash")
            except Exception as e2:
                print(f"⚠️ Failed to load gemini-1.5-flash: {e2}")
                # Dynamic fallback to first available
                models = genai.list_models()
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        self.model = genai.GenerativeModel(model.name)
                        print(f"✅ Fallback model: {model.name}")
                        break
                else:
                    raise Exception("No Gemini models available that support generateContent")
    
    def generate_text(self, prompt, max_tokens=500, max_retries=3):
        for attempt in range(max_retries):
            try:
                # Clean the prompt and limit length
                clean_prompt = prompt[:4000]  # Limit prompt length
                
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": max_tokens,
                }
                
                response = self.model.generate_content(
                    clean_prompt,
                    generation_config=generation_config
                )
                return response.text.strip()
            
            except Exception as e:
                error_str = str(e)
                print(f"Gemini API Error (attempt {attempt + 1}/{max_retries}): {error_str}")
                
                # Handle quota exceeded (429) with backoff
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 30  # Exponential: 30s, 60s, 120s
                        print(f"⏳ Quota hit—retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "AI quota exceeded (429). Upgrade to paid tier or wait 24h. Tip: Use fewer emails to reduce calls."
                else:
                    # Other errors (e.g., 404 model): No retry
                    return f"AI service unavailable: {error_str}"
        
        return "Max retries exceeded due to quota issues. Please check your API limits."
    
    def chat(self, message, chat_history=None):
        try:
            if chat_history is None:
                chat_history = []
            
            chat = self.model.start_chat(history=chat_history)
            response = chat.send_message(message)
            return response.text, chat.history
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                return "Quota exceeded—try a simple query or wait.", chat_history
            return f"Chat error: {str(e)}", chat_history