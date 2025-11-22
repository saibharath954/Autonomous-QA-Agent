# app/services/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingService:
    """
    Wrapper around a SentenceTransformer model.
    Produces fixed-size float32 numpy embeddings for a list of texts.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        texts -> numpy array shape (n_texts, dim)
        """
        # SentenceTransformer returns np.ndarray of dtype float32
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # Ensure dtype float32
        return embeddings.astype("float32")
