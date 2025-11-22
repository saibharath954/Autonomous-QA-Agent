import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import EmbeddingService
texts = ["hello world", "this is a test"]
e = EmbeddingService()
embs = e.embed_texts(texts)
print("shape:", embs.shape)
print("dtype:", embs.dtype)
