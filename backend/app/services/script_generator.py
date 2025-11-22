import os
from typing import Dict, Any
from app.services.llm_provider import LLMProvider
from app.services.vector_db import VectorDB

class ScriptGeneratorService:
    def __init__(self):
        self.llm = LLMProvider()
        # We access VectorDB just in case we need extra doc context, 
        # but primarily we need the raw HTML file for selectors.
        self.vector_db = VectorDB()

    def _get_html_content(self) -> str:
        """
        Retrieves the raw HTML content of checkout.html.
        In a real app, this might come from the DB, but for this assignment,
        we look in the uploaded_docs folder as per the setup.
        """
        # Check common paths
        possible_paths = [
            "uploaded_docs/checkout.html", 
            "../uploaded_docs/checkout.html",
            "./checkout.html"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        
        return ""

    def generate_script(self, test_case: Dict[str, Any]) -> str:
        # 1. Get the Target HTML (Crucial for accurate selectors)
        html_content = self._get_html_content()
        
        # 2. Construct the Prompt
        # Strict requirements from PDF: "Use appropriate selectors... based on actual HTML" [cite: 135]
        system_prompt = """
        You are a Senior QA Automation Engineer specializing in Python and Selenium.
        Your task is to convert a functional test case into a robust, executable Selenium script.
        
        STRICT RULES:
        1. Analyze the provided HTML code deeply to find the EXACT IDs, Names, or CSS Selectors.
        2. Do NOT invent element IDs that do not exist in the provided HTML.
        3. The script must be a standalone Python file including `import unittest` and `from selenium import webdriver`.
        4. Use `webdriver.Chrome()` (headless mode optional but recommended).
        5. Include assertions that match the "Expected Result" in the test case.
        6. Return ONLY the Python code. No markdown formatting, no explanations outside the code.
        """

        user_prompt = f"""
        ### TARGET HTML:
        {html_content}

        ### TEST CASE TO AUTOMATE:
        Feature: {test_case.get('Feature')}
        Scenario: {test_case.get('Test_Scenario')}
        Expected Result: {test_case.get('Expected_Result')}

        ### INSTRUCTION:
        Write the Selenium script now.
        """

        # 3. Call LLM
        raw_response = self.llm.generate_response(system_prompt, user_prompt)
        
        # Clean formatting if LLM adds ```python blocks
        clean_code = raw_response.replace("```python", "").replace("```", "").strip()
        
        return clean_code