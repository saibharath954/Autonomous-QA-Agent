import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.file_ingestion import process_local_file

# Path to your PDF inside backend/uploaded_docs
local_pdf_path = "uploaded_docs/E-Shop Checkout System.pdf"

item = process_local_file(local_pdf_path)
text = item["text"]
meta = item["metadata"]

kb = KnowledgeBaseBuilder(persist_dir="./chroma_db")
result = kb.build_from_texts([{
    "source": meta["source"],
    "text": text,
    "type": meta["type"]
}])

print("KB build result:", result)
