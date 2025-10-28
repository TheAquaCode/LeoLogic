"""
Mistral API Client
"""

from mistralai import Mistral
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, MAX_CONVERSATION_HISTORY


class MistralChatbot:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise RuntimeError("❌ MISTRAL_API_KEY not set in environment variables.")
        
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.conversation_history = []
        self.is_ready = True
        self.loading = False
        self.system_instruction = (
            "You are a helpful chatbot for an AI file sorter application. "
            "Be concise and friendly."
        )

    def generate_response(self, user_message, store_history=True):
        """Send conversation to Mistral API and get the response"""
        try:
            # Build messages
            messages = [{"role": "system", "content": self.system_instruction}]
            
            # Add conversation history (last N exchanges)
            for msg in self.conversation_history[-MAX_CONVERSATION_HISTORY:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call Mistral API
            chat_response = self.client.chat.complete(
                model=MISTRAL_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )

            # Extract response
            response_text = chat_response.choices[0].message.content

            # Save to history
            if store_history:
                self.conversation_history.append({
                    "user": user_message,
                    "assistant": response_text
                })

            return response_text

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
