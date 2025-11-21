import json
import fitz  # PyMuPDF
from fastapi import UploadFile
from app.utils.parser_utils import parse_html

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
