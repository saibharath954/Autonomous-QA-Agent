# app/services/kb_builder.py
from typing import List, Dict, Any
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDB
from app.utils.chunk_utils import chunk_text
import os
from tqdm import tqdm

class KnowledgeBaseBuilder:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.embedder = EmbeddingService()
        self.vdb = VectorDB(persist_dir=persist_dir)

    def build_from_texts(self, texts: List[Dict[str, Any]], session_id: str, chunk_size: int = 800, chunk_overlap: int = 150):
        """
        texts: list of dicts { "source": filename, "text": "...", "type": "pdf|html|json|text" }
        This will chunk each text, create embeddings, and add chunks to the vector DB with metadata.
        """
        all_chunks = []
        all_metas = []
        for doc in texts:
            source = doc.get("source", "unknown")
            text = doc.get("text", "")
            doc_type = doc.get("type", "text")
            chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            for i, chunk in enumerate(chunks):
                meta = {
                    "source": source,
                    "type": doc_type,
                    "chunk_index": i,
                    "chunk_size_est": len(chunk),
                    "session_id": session_id
                }
                all_chunks.append(chunk)
                all_metas.append(meta)

        if not all_chunks:
            return {"status": "no_chunks", "added": 0}

        # Create embeddings in batches to avoid memory spikes
        batch_size = 64
        embeddings = []
        for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding batches"):
            batch = all_chunks[i:i + batch_size]
            emb = self.embedder.embed_texts(batch)
            embeddings.extend(emb.tolist())

        # Add to vector DB
        self.vdb.add_documents(texts=all_chunks, embeddings=embeddings, metadatas=all_metas)
        self.vdb.persist()
        return {"status": "ok", "added": len(all_chunks)}
