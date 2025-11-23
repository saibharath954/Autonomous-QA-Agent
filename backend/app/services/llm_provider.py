import os
import json
import requests  # pip install requests
from groq import Groq  # pip install groq
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    def __init__(self, provider="groq", model_name="llama-3.3-70b-versatile"):
        self.provider = provider
        self.model_name = model_name
        self.client = None
        
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                # Fallback to Ollama if Groq key is missing, or raise warning
                print("⚠️ GROQ_API_KEY not found. Ensure you set it if using Groq.")
            else:
                self.client = Groq(api_key=api_key)
        
        # Ollama doesn't need a client init for HTTP requests, 
        # but we can set the base URL
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate_response(self, system_prompt: str, user_content: str) -> str:
        """
        Sends request to LLM (Groq or Ollama) and returns raw string response.
        """
        try:
            if self.provider == "groq":
                if not self.client:
                    return "Error: Groq client not initialized (missing API Key)."
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    model=self.model_name,
                    temperature=0.1,  # Low temp for precision
                )
                return chat_completion.choices[0].message.content

            elif self.provider == "ollama":
                # Robust Ollama Implementation via HTTP
                payload = {
                    "model": "llama3",  # Ensure you have 'llama3' pulled in Ollama
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "stream": False
                }
                response = requests.post(f"{self.ollama_base_url}/api/chat", json=payload)
                
                if response.status_code == 200:
                    return response.json()["message"]["content"]
                else:
                    return f"Error from Ollama: {response.text}"

        except Exception as e:
            return f"Error interacting with LLM: {str(e)}"