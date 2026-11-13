"""
search.py (schemas) — shape of document-search (RAG retrieval) results.
"""

from pydantic import BaseModel


class SearchHit(BaseModel):
    rank: int
    score: float
    chunk_id: str
    document: str
    section: str
    text: str


class SearchResponse(BaseModel):
    query: str
    # All three rankings side by side, so you can COMPARE the methods.
    bm25: list[SearchHit]
    dense: list[SearchHit]
    hybrid_rrf: list[SearchHit]
