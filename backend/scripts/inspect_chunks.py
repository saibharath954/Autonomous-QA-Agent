import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.kb_builder import KnowledgeBaseBuilder
from app.services.file_ingestion import process_local_file
from app.services.vector_db import VectorDB
from app.services.embeddings import EmbeddingService

item = process_local_file("uploaded_docs/E-Shop Checkout System.pdf")
kb = KnowledgeBaseBuilder(persist_dir="./chroma_db")
# We assume KB already built; to read the DB we use VectorDB directly:
vdb = VectorDB(persist_dir="./chroma_db")
# Chroma collection exposes .get method through query without embedding
# We'll just query with a dummy vector of zeros if needed; better: embed a short query
embed = EmbeddingService()
q = "discount code"
q_emb = embed.embed_texts([q])[0].tolist()
results = vdb.query(q_emb, n_results=5)
for r in results:
    print("-----")
    print("ID:", r['id'])
    print("Source:", r['metadata'].get('source'))
    print("Chunk size:", r['metadata'].get('chunk_size_est'))
    print(r['document'][:600])
