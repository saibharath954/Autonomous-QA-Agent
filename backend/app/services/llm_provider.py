import os
import json
from typing import Dict, Any, List
from groq import Groq  # pip install groq
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLMProvider:
    def __init__(self, provider="groq", model_name="llama-3.3-70b-versatile"):
        self.provider = provider
        self.model_name = model_name
        self.client = None
        
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")
            self.client = Groq(api_key=api_key)

    def generate_response(self, system_prompt: str, user_content: str) -> str:
        """
        Sends request to LLM and returns raw string response.
        """
        try:
            if self.provider == "groq":
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    model=self.model_name,
                    temperature=0.1, # Low temp for factual accuracy
                )
                return chat_completion.choices[0].message.content
            
            # Placeholder for Ollama implementation
            # elif self.provider == "ollama":
            #     import requests
            #     res = requests.post("http://localhost:11434/api/generate", ...)
            #     return res.json()["response"]

        except Exception as e:
            return f"Error interacting with LLM: {str(e)}"