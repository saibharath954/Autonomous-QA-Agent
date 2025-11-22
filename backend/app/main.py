from fastapi import FastAPI, APIRouter, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from app.services.file_ingestion import process_uploaded_file, process_local_file
from app.services.vector_db import VectorDB
from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.rag_service import RAGService  # <--- Import RAG Service
from app.services.script_generator import ScriptGeneratorService

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
script_gen_service = ScriptGeneratorService()

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

# --- UPDATED ENDPOINT ---
@app.post("/generate-selenium-script")
async def generate_script(testcase_json: str = Form(...)):
    """
    Receives a single test case JSON string.
    Returns generated Python code.
    """
    import json
    try:
        # Parse the JSON string back to a dict
        test_case_dict = json.loads(testcase_json)
        
        # Generate Code
        script = script_gen_service.generate_script(test_case_dict)
        
        return {"script": script}
    except Exception as e:
        return {"error": str(e)}

app.include_router(router)