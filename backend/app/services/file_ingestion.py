# app/services/file_ingestion.py
import json
import fitz  # PyMuPDF
from fastapi import UploadFile
from app.utils.parser_utils import parse_html
from typing import Dict, Any
import os

async def process_uploaded_file(file: UploadFile):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        doc = fitz.open(stream=await file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        metadata = {"source": filename, "type": "pdf"}

    elif filename.endswith(".json"):
        content = json.loads((await file.read()).decode("utf-8"))
        text = json.dumps(content, indent=2)
        metadata = {"source": filename, "type": "json"}

    elif filename.endswith(".html"):
        raw = (await file.read()).decode("utf-8")
        text = parse_html(raw)
        metadata = {"source": filename, "type": "html"}

    else:
        text = (await file.read()).decode("utf-8")
        metadata = {"source": filename, "type": "text"}

    return text, metadata

def process_local_file(path: str) -> Dict[str, Any]:
    """
    Helper for local/dev usage when you have a filepath
    Returns dict: { "text": <extracted>, "metadata": {source, type} }
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    filename = os.path.basename(path).lower()

    if filename.endswith(".pdf"):
        import fitz
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        metadata = {"source": filename, "type": "pdf"}
    elif filename.endswith(".json"):
        with open(path, "r", encoding="utf-8") as fh:
            content = json.load(fh)
        text = json.dumps(content, indent=2)
        metadata = {"source": filename, "type": "json"}
    elif filename.endswith(".html"):
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
        text = parse_html(raw)
        metadata = {"source": filename, "type": "html"}
    else:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        metadata = {"source": filename, "type": "text"}

    return {"text": text, "metadata": metadata}
