from fastapi import FastAPI, APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.services.file_ingestion import process_uploaded_file
from app.services.vector_db import VectorDB
from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.rag_service import RAGService
from app.services.script_generator import ScriptGeneratorService

app = FastAPI(title="Autonomous QA Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
# Note: In production, vector_db might be a cloud instance (Pinecone/Weaviate)
kb_builder = KnowledgeBaseBuilder(persist_dir="./chroma_db")
rag_service = RAGService(persist_dir="./chroma_db")
script_gen_service = ScriptGeneratorService()

@app.get("/")
def home():
    return {"message": "QA Agent Backend Running"}

@app.post("/upload-documents")
async def upload_documents(
    files: List[UploadFile] = File(...),
    x_session_id: str = Header(..., alias="X-Session-ID") # Enforce Header
):
    """
    Production Endpoint: Accepts multiple files, extracts text,
    saves html with session id suffix, and builds the Knowledge Base immediately.
    """
    processed_docs = []
    saved_html_filenames = []
    headers = {"X-Session-ID": x_session_id}

    for file in files:
        try:
            filename = file.filename
            lower = filename.lower()
            # Save HTML files explicitly with session id to avoid conflicts
            if lower.endswith(".html") or lower.endswith(".htm"):
                safe_name = f"{os.path.splitext(filename)[0]}__{x_session_id}.html"
                save_path = os.path.join("uploaded_docs", safe_name)
                with open(save_path, "wb") as fh:
                    content = await file.read()
                    fh.write(content)
                # also add to processed_docs as HTML text to be ingested
                html_text = content.decode("utf-8", errors="ignore")
                processed_docs.append({
                    "source": safe_name,
                    "text": html_text,
                    "type": "html"
                })
                saved_html_filenames.append(safe_name)
            else:
                # Non-HTML files: existing processing path
                text, meta = await process_uploaded_file(file)
                processed_docs.append({
                    "source": meta["source"],
                    "text": text,
                    "type": meta["type"]
                })
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            continue

    if not processed_docs:
        raise HTTPException(status_code=400, detail="No valid documents processed")

    # Build KB immediately with all processed docs (including html)
    result = kb_builder.build_from_texts(processed_docs, session_id=x_session_id)

    return {
        "status": "success",
        "processed_files": [d["source"] for d in processed_docs],
        "saved_html_files": saved_html_filenames,
        "kb_build_result": result
    }


@app.post("/generate-testcases")
async def generate_testcases(
    query: str = Form(...),
    x_session_id: str = Header(..., alias="X-Session-ID") # Enforce Header
):
    results = rag_service.generate_test_cases(query, session_id=x_session_id)
    return {"results": results}

@app.post("/generate-selenium-script")
async def generate_script(
    testcase_json: str = Form(...),
    x_session_id: str = Header(..., alias="X-Session-ID")
):
    import json
    try:
        test_case_dict = json.loads(testcase_json)
        script = script_gen_service.generate_script(test_case_dict, session_id=x_session_id)
        return {"script": script}
    except Exception as e:
        return {"error": str(e)}

# Ensure uploaded_docs exists for the HTML file save
import os
os.makedirs("uploaded_docs", exist_ok=True)