import os
import json
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from app.services.llm_provider import LLMProvider
from app.services.vector_db import VectorDB


class ScriptGeneratorService:
    def __init__(self, upload_dir: str = "uploaded_docs"):
        self.upload_dir = upload_dir
        self.llm = LLMProvider()
        self.vector_db = VectorDB()  # Only for extra text docs if needed

    # ------------------------------------------------------
    # Load the session-specific HTML file
    # ------------------------------------------------------
    def _load_session_html(self, session_id: str) -> Optional[str]:
        """
        Loads the correct HTML file for this session.
        Files are saved in the format:
            checkout__<session_id>.html
        """
        for fname in os.listdir(self.upload_dir):
            if fname.endswith(f"__{session_id}.html"):
                path = os.path.join(self.upload_dir, fname)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        return None

    # ------------------------------------------------------
    # Extract useful selector metadata from HTML
    # ------------------------------------------------------
    def _extract_html_metadata(self, html: str) -> Dict:
        soup = BeautifulSoup(html, "html.parser")

        inputs = []
        for element in soup.find_all(["input", "select", "textarea"]):
            inputs.append({
                "tag": element.name,
                "type": element.get("type"),
                "id": element.get("id"),
                "name": element.get("name"),
                "class": element.get("class"),
                "placeholder": element.get("placeholder"),
                "text": element.get_text(strip=True)
            })

        buttons = []
        for btn in soup.find_all(["button", "input"]):
            if btn.name == "button" or (btn.name == "input" and btn.get("type") in ["submit", "button"]):
                buttons.append({
                    "tag": btn.name,
                    "id": btn.get("id"),
                    "name": btn.get("name"),
                    "class": btn.get("class"),
                    "text": btn.get_text(strip=True) or btn.get("value")
                })

        return {
            "inputs": inputs,
            "buttons": buttons
        }

    # ------------------------------------------------------
    # Build prompt with strong grounding
    # ------------------------------------------------------
    def _build_prompt(self, test_case: Dict, html_raw: str, meta: Dict) -> str:
        system_prompt = """
        You are a Senior QA Automation Engineer specializing in Selenium (Python).

        STRICT RULES:
        1. Use ONLY the selectors that exist in the provided HTML.
        2. Prefer ID → Name → CSS selectors.
        3. Never hallucinate IDs or names.
        4. Use selenium.webdriver + WebDriverWait + By.
        5. Output ONLY Python code. No explanations.
        """

        user_prompt = f"""
        ### RAW HTML OF THE PAGE:
        {html_raw}

        ### EXTRACTED ELEMENT METADATA:
        {json.dumps(meta, indent=2)}

        ### TEST CASE:
        Feature: {test_case.get("Feature")}
        Scenario: {test_case.get("Test_Scenario")}
        Expected Result: {test_case.get("Expected_Result")}

        ### INSTRUCTION:
        Generate a complete runnable Python Selenium script implementing this test.
        """

        return system_prompt, user_prompt

    # ------------------------------------------------------
    # Generate Final Selenium Script
    # ------------------------------------------------------
    def generate_script(self, test_case: Dict[str, Any], session_id: str) -> str:
        # Load correct HTML
        html_raw = self._load_session_html(session_id)

        if not html_raw:
            return "# ERROR: No HTML file found for this session."

        # Extract metadata
        meta = self._extract_html_metadata(html_raw)

        # Build prompt
        system_prompt, user_prompt = self._build_prompt(test_case, html_raw, meta)

        # LLM call
        raw_output = self.llm.generate_response(system_prompt, user_prompt)

        # Clean ```python code fences
        clean = raw_output.replace("```python", "").replace("```", "").strip()

        return clean
