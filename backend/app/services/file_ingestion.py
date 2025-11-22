import json
import fitz  # PyMuPDF
import os
from fastapi import UploadFile
from app.utils.parser_utils import parse_html
from typing import Tuple, Dict, Any

async def process_uploaded_file(file: UploadFile) -> Tuple[str, Dict[str, Any]]:
    """
    Reads an uploaded file directly from memory/stream and extracts text.
    Returns: (extracted_text, metadata)
    """
    filename = file.filename.lower()
    content = await file.read() # Read file bytes
    
    text = ""
    metadata = {"source": filename, "type": "unknown"}

    if filename.endswith(".pdf"):
        # Open PDF from bytes
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        metadata["type"] = "pdf"

    elif filename.endswith(".json"):
        data = json.loads(content.decode("utf-8"))
        text = json.dumps(data, indent=2)
        metadata["type"] = "json"

    elif filename.endswith(".html"):
        raw_html = content.decode("utf-8")
        text = parse_html(raw_html)
        metadata["type"] = "html"
        
        # PRODUCTION CHANGE: Save HTML locally briefly so ScriptGenerator can read it later
        # In a real cloud app, you'd save this to S3. 
        # overwriting a 'current_checkout.html' as a trade-off.
        with open("uploaded_docs/checkout.html", "w", encoding="utf-8") as f:
            f.write(raw_html)

    else: # txt, md, etc.
        text = content.decode("utf-8")
        metadata["type"] = "text"

    # Reset file cursor just in case
    await file.seek(0)
    
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
