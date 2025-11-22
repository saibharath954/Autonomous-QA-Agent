import json
import re
from typing import List, Dict, Any
from app.services.vector_db import VectorDB
from app.services.embeddings import EmbeddingService
from app.services.llm_provider import LLMProvider

class RAGService:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.vector_db = VectorDB(persist_dir=persist_dir)
        self.embedder = EmbeddingService()
        self.llm = LLMProvider()  # Defaults to Groq

    def generate_test_cases(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Embed User Query
        query_embedding = self.embedder.embed_texts([query])[0].tolist()

        # 2. Retrieve Relevant Chunks
        results = self.vector_db.query(query_embedding, n_results=k)
        
        if not results:
            return {"error": "No relevant documents found in Knowledge Base."}

        # 3. Format Context
        # We concatenate snippets with their source to allow "Grounded_In" citation
        context_str = ""
        for i, doc in enumerate(results):
            source = doc['metadata'].get('source', 'Unknown')
            text = doc['document']
            context_str += f"--- SOURCE {i+1}: {source} ---\n{text}\n\n"

        # 4. Construct Strict System Prompt (Based on Assignment-1 Page 4 & 5)
        system_prompt = """
        You are an intelligent QA Agent. Your goal is to generate comprehensive test cases based STRICTLY on the provided context.
        
        RULES:
        1. Use ONLY the provided "Context" to generate test cases. Do not hallucinate features not mentioned.
        2. Output must be a valid JSON array of objects.
        3. Each object must have exactly these keys:
           - "Test_ID": (e.g., TC-001)
           - "Feature": (The feature being tested)
           - "Test_Scenario": (Action to perform)
           - "Expected_Result": (The documented outcome)
           - "Grounded_In": (The exact filename from the context where this rule is found)
        
        If the context does not contain enough information to answer the query, return an empty JSON array [].
        """

        user_prompt = f"""
        Context:
        {context_str}

        User Query: "{query}"
        
        Generate the test cases in JSON format now:
        """

        # 5. Call LLM
        raw_response = self.llm.generate_response(system_prompt, user_prompt)

        # 6. Parse JSON (Clean up markdown formatting if present)
        try:
            # Remove ```json ... ``` if the LLM adds it
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(clean_json)
            return parsed_data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse LLM response", 
                "raw_response": raw_response
            }