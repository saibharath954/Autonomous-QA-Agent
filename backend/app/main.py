from fastapi import FastAPI, APIRouter, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from app.services.file_ingestion import process_uploaded_file, process_local_file
from app.services.vector_db import VectorDB
from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.rag_service import RAGService  # <--- Import RAG Service

app = FastAPI(title="Autonomous QA Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
vector_db = VectorDB()
kb_builder = KnowledgeBaseBuilder(persist_dir="./chroma_db")
rag_service = RAGService(persist_dir="./chroma_db") # <--- Initialize

router = APIRouter()

@app.get("/")
def home():
    return {"message": "QA Agent Backend Running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    text, metadata = await process_uploaded_file(file)
    return {"filename": file.filename, "extracted_length": len(text)}

@app.post("/build-kb")
async def build_kb():
    # In a real app, this might trigger a rebuild or be redundant if we build on upload
    # checking if vector_db has data is a good check here
    return {"status": "Knowledge Base Accessible"}

@router.post("/build-kb-from-uploaded-path")
def build_kb_from_path(path: str = Body(..., embed=True)):
    item = process_local_file(path)
    res = kb_builder.build_from_texts([{
        "source": item["metadata"]["source"],
        "text": item["text"],
        "type": item["metadata"]["type"]
    }])
    return res

# --- NEW ENDPOINT ---
@app.post("/generate-testcases")
async def generate_testcases(query: str = Form(...)):
    """
    Accepts a query (e.g., 'Generate test cases for discount code')
    Returns JSON list of test cases.
    """
    results = rag_service.generate_test_cases(query)
    return {"results": results}
# --------------------

@app.post("/generate-selenium-script")
async def generate_script(testcase_json: str = Form(...)):
    # Placeholder for Phase 3
    return {"status": "Selenium script generator endpoint ready"}

app.include_router(router)