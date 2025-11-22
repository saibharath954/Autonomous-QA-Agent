# scripts/query_kb.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDB

embed = EmbeddingService()
vdb = VectorDB(persist_dir="./chroma_db")

query = "discount code SAVE15 applies 15% discount"
q_emb = embed.embed_texts([query])[0].tolist()
results = vdb.query(q_emb, n_results=5)
for r in results:
    print("----")
    print("distance:", r["distance"])
    print("source:", r["metadata"].get("source"))
    print("text snippet:", r["document"][:500])
