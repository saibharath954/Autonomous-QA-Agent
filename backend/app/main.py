from fastapi import Body, FastAPI, APIRouter, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services.file_ingestion import process_uploaded_file
from app.services.vector_db import VectorDB
from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.file_ingestion import process_local_file

app = FastAPI(title="Autonomous QA Agent Backend")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector DB
vector_db = VectorDB()

router = APIRouter()
kb_builder = KnowledgeBaseBuilder(persist_dir="./chroma_db")

@router.post("/build-kb-from-uploaded-path")
def build_kb_from_path(path: str = Body(..., embed=True)):
    """
    Accepts JSON like: {"path":"uploaded_docs/E-Shop Checkout System.pdf"}
    or call as a query param: POST /build-kb-from-uploaded-path?path=...
    """
    item = process_local_file(path)
    res = kb_builder.build_from_texts([{
        "source": item["metadata"]["source"],
        "text": item["text"],
        "type": item["metadata"]["type"]
    }])
    return res

# IMPORTANT: include the router so routes are registered
app.include_router(router)

@app.get("/")
def home():
    return {"message": "QA Agent Backend Running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    text, metadata = await process_uploaded_file(file)
    return {"filename": file.filename, "extracted_length": len(text)}

@app.post("/build-kb")
async def build_kb():
    vector_db.build()
    return {"status": "Knowledge Base Built Successfully"}

@app.post("/generate-testcases")
async def generate_testcases(query: str = Form(...)):
    # Placeholder - to be implemented in later phases
    return {"status": "Test case generation endpoint ready"}

@app.post("/generate-selenium-script")
async def generate_script(testcase_json: str = Form(...)):
    # Placeholder
    return {"status": "Selenium script generator endpoint ready"}
