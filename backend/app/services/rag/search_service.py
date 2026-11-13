"""
search_service.py — runs BM25 + dense search and FUSES them with RRF.

CONCEPT — RAG (Retrieval-Augmented Generation):
  R = Retrieve: find the most relevant document chunks   <- THIS FILE
  A = Augment : paste those chunks into the LLM prompt    <- assistant
  G = Generate: the LLM writes an answer using them       <- assistant
  ANALOGY: an open-book exam. The LLM doesn't need to have memorised our
  policies; we hand it the right pages and it answers from them.

CONCEPT — RRF (Reciprocal Rank Fusion):
  BM25 scores (like 4.7) and cosine scores (like 0.62) use different
  scales, so we can't just add them. RRF ignores the scores and uses only
  the RANK positions:
        rrf_score(chunk) = sum over methods of  1 / (k + rank)
  ANALOGY: two judges each rank the contestants. A contestant ranked
  high by BOTH judges wins overall, even if neither ranked them #1.
  k = 60 is the standard value. It stops the #1 spot from dominating.
"""

from threading import Lock

from app.services.ingestion.document_loader import Chunk, load_chunks
from app.services.rag.bm25 import BM25Index
from app.services.rag.dense import DenseIndex

RRF_K = 60


class SearchEngine:
    def __init__(self):
        self.chunks: list[Chunk] = load_chunks()
        texts = [c.text for c in self.chunks]
        self.bm25 = BM25Index(texts)
        self.dense = DenseIndex(texts)

    @staticmethod
    def _ranked(scores: list[float], keep_zero: bool) -> list[tuple[int, float]]:
        """[(chunk_index, score), ...] best first. BM25 drops 0-score (no word match)."""
        pairs = [(i, s) for i, s in enumerate(scores) if keep_zero or s > 0]
        return sorted(pairs, key=lambda p: p[1], reverse=True)

    def _hits(self, ranked: list[tuple[int, float]], top_k: int) -> list[dict]:
        """Turn (index, score) pairs into JSON-friendly result dicts."""
        return [
            {
                "rank": position,
                "score": round(score, 4),
                "chunk_id": self.chunks[i].chunk_id,
                "document": self.chunks[i].document,
                "section": self.chunks[i].section,
                "text": self.chunks[i].text,
            }
            for position, (i, score) in enumerate(ranked[:top_k], start=1)
        ]

    def search(self, query: str, top_k: int = 3) -> dict:
        bm25_ranked = self._ranked(self.bm25.scores(query), keep_zero=False)
        dense_ranked = self._ranked(self.dense.scores(query), keep_zero=True)

        # RRF: add 1/(k + rank) from every list the chunk appears in.
        fused: dict[int, float] = {}
        for ranked in (bm25_ranked, dense_ranked):
            for rank, (i, _score) in enumerate(ranked, start=1):
                fused[i] = fused.get(i, 0.0) + 1.0 / (RRF_K + rank)
        hybrid_ranked = sorted(fused.items(), key=lambda p: p[1], reverse=True)

        return {
            "query": query,
            "bm25": self._hits(bm25_ranked, top_k),
            "dense": self._hits(dense_ranked, top_k),
            "hybrid_rrf": self._hits(hybrid_ranked, top_k),
        }


# ---- Singleton: build the index ONCE and reuse it for every request. ----
# Loading the embedding model takes a few seconds, so we don't redo it per call.
# The Lock makes sure two first requests at the same moment don't both build it.
_engine: SearchEngine | None = None
_lock = Lock()


def get_search_engine() -> SearchEngine:
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                _engine = SearchEngine()
    return _engine
