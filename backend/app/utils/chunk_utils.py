# app/utils/chunk_utils.py
from typing import List
import math

try:
    # prefer langchain splitter for robust splits
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    _HAS_LANGCHAIN = True
except Exception:
    _HAS_LANGCHAIN = False

def chunk_text_langchain(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def simple_chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    """
    Fallback chunker: splits at nearest newline/space to produce chunks with overlap.
    """
    if not text:
        return []
    words = text.split()
    out = []
    i = 0
    n = len(words)
    while i < n:
        end = min(n, i + chunk_size)
        chunk = " ".join(words[i:end])
        out.append(chunk)
        i = end - chunk_overlap if (end - chunk_overlap) > i else end
    return out

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150):
    if _HAS_LANGCHAIN:
        try:
            return chunk_text_langchain(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        except Exception:
            return simple_chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        return simple_chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
