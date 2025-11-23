# app/services/vector_db.py
import chromadb
from typing import List, Dict, Any, Optional
import os
import uuid

class VectorDB:
    """
    Simple wrapper around Chroma to store embeddings + documents + metadata.
    Provides a stable query() that normalizes results across Chroma versions.
    """

    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "qa_agent"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        # Ensure directory exists
        os.makedirs(self.persist_dir, exist_ok=True)

        # Setup Chroma client with persistence (new API)
        # If your chroma version differs, this should still work for local persistent usage.
        self.client = chromadb.PersistentClient(path=self.persist_dir)

        # create or get collection without embedding_function (we will add explicit embeddings)
        try:
            # try to get collection; some versions raise if not found
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            # fallback: create it
            self.collection = self.client.create_collection(name=self.collection_name)

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """
        Add lists of texts (documents/chunks), their embeddings, and metadata to Chroma.
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # Chroma expects lists
        self.collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_embedding: List[float], n_results: int = 5, session_id: str = None) -> List[Dict[str, Any]]:
        """
        Query by embedding: returns list of dicts with 'id', 'document', 'metadata', 'distance'

        This method is defensive: it accepts different Chroma versions that may return
        results under different keys (e.g. 'ids' vs 'data') and will normalize them.
        """
        # Preferred includes (avoid 'ids' which some Chroma versions reject)
        include = ['metadatas', 'documents', 'distances']

        # CRITICAL FIX: Add the 'where' filter
        where_filter = {"session_id": session_id} if session_id else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=include,
            where=where_filter  # <--- This prevents cross-contamination
        )

        # results expected to be dict of lists (one entry per query)
        if not results:
            return []

        # helper to safely extract the single-query lists (or fallbacks)
        def first_or_empty(key):
            val = results.get(key)
            if val is None:
                return []
            # some versions return list-of-lists (one per query)
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], list):
                return val[0]
            # some versions may already return a flat list
            return val

        # try common keys
        ids = first_or_empty('ids') or first_or_empty('data') or []
        docs = first_or_empty('documents') or []
        metas = first_or_empty('metadatas') or []
        distances = first_or_empty('distances') or []

        # If Chroma returned a different structure, try to inspect 'documents' under 'data'
        if not docs and ids and isinstance(ids[0], (list, tuple)):
            # rare case: nested further, try flattening first element
            ids = ids[0]

        # Normalize lengths: the lists should be same length; if not, use min length
        length = min(
            [len(lst) for lst in (ids, docs, metas, distances) if isinstance(lst, list)] or [0]
        )

        out = []
        for i in range(length):
            out.append({
                'id': ids[i] if i < len(ids) else None,
                'document': docs[i] if i < len(docs) else None,
                'metadata': metas[i] if i < len(metas) else {},
                'distance': distances[i] if i < len(distances) else None
            })
        return out

    def persist(self):
        """
        Persist the DB to disk (Chroma duckdb+parquet uses automatic persistence, but call for clarity).
        """
        try:
            # PersistentClient may not expose persist() in all versions; guard it
            if hasattr(self.client, "persist"):
                self.client.persist()
        except Exception:
            pass

    def reset_collection(self):
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self.collection = self.client.create_collection(name=self.collection_name)
