import json
import re  # <--- Import Regex
from typing import List, Dict, Any
from app.services.vector_db import VectorDB
from app.services.embeddings import EmbeddingService
from app.services.llm_provider import LLMProvider

class RAGService:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.vector_db = VectorDB(persist_dir=persist_dir)
        self.embedder = EmbeddingService()
        self.llm = LLMProvider() 

    # UPDATED: Accept session_id
    def generate_test_cases(self, query: str, session_id: str, k: int = 5,) -> List[Dict[str, Any]]:
        # 1. Embed & Retrieve (Same as before)
        query_embedding = self.embedder.embed_texts([query])[0].tolist()
        results = self.vector_db.query(query_embedding, n_results=k, session_id=session_id)
        
        # If absolutely no docs found in DB
        if not results:
            return [{"error": "Knowledge Base is empty or no matches found."}]

        context_str = ""
        for i, doc in enumerate(results):
            source = doc['metadata'].get('source', 'Unknown')
            text = doc['document']
            context_str += f"--- SOURCE {i+1}: {source} ---\n{text}\n\n"

        # 2. Strict System Prompt
        system_prompt = """
        You are an intelligent QA Agent. Your goal is to generate comprehensive test cases based STRICTLY on the provided context.

        OUTPUT RULES:
        1. Use ONLY the provided "Context" to generate test cases. Do not hallucinate features not mentioned.
        2. Output must be a valid JSON array of objects.
        3. Do NOT add markdown formatting (like ```json).
        4. Do NOT add conversational text or explanations.
        5. If the context has no relevant info, return exactly: []
        
        JSON Structure:
        [
          {
            "Test_ID": "TC-001",
            "Feature": "The feature being tested",
            "Test_Scenario": "Action to perform",
            "Expected_Result": "Expected outcome of the test",
            "Grounded_In": "The exact filename from the context where this rule is found"
          }
        ]
        """

        user_prompt = f"""
        Context:
        {context_str}

        User Query: "{query}"
        """

        # 3. Call LLM
        raw_response = self.llm.generate_response(system_prompt, user_prompt)

        # 4. ROBUST PARSING LOGIC (The Fix)
        try:
            # Step A: Remove Markdown code blocks if present
            clean_text = raw_response.replace("```json", "").replace("```", "").strip()

            # Step B: Use Regex to find the JSON array [...]
            # This handles cases where LLM says: "Here is the JSON: [...]"
            json_match = re.search(r'\[.*\]', clean_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)
                return parsed_data
            
            # Step C: If no JSON array found, check if it's an empty response or error explanation
            if "context" in clean_text.lower() and "contain" in clean_text.lower():
                 # The LLM is explaining why it failed. Return empty list.
                 return []
            
            # Fallback
            return [{"error": "LLM returned invalid format", "raw": clean_text}]

        except json.JSONDecodeError:
            return [{"error": "Failed to parse JSON", "raw": raw_response}]