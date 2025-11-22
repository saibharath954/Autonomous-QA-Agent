import pytest
from app.services.file_ingestion import process_local_file
from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDB

def test_process_local_file():
    item = process_local_file("uploaded_docs/E-Shop Checkout System.pdf")
    assert item["text"] and isinstance(item["text"], str)
    assert "source" in item["metadata"]

def test_embedding_shape():
    e = EmbeddingService()
    v = e.embed_texts(["one", "two"])
    assert v.shape[0] == 2
    assert v.dtype.name == "float32"

def test_build_kb_and_query(tmp_path):
    kb = KnowledgeBaseBuilder(persist_dir=str(tmp_path/"chroma_db"))
    item = process_local_file("uploaded_docs/E-Shop Checkout System.pdf")
    res = kb.build_from_texts([{"source": item["metadata"]["source"], "text": item["text"], "type": item["metadata"]["type"]}])
    assert res["status"] == "ok"
    vdb = VectorDB(persist_dir=str(tmp_path/"chroma_db"))
    e = EmbeddingService()
    q_emb = e.embed_texts(["discount code"])[0].tolist()
    results = vdb.query(q_emb, n_results=3)
    assert isinstance(results, list)
