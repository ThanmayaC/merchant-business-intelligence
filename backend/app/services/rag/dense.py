"""
dense.py — MEANING-based search with Sentence-Transformers embeddings.

CONCEPT — Embeddings:
  An embedding model turns a sentence into a list of numbers (a "vector").
  all-MiniLM-L6-v2 makes 384 numbers per sentence. Sentences with SIMILAR
  MEANING get vectors that point in a SIMILAR DIRECTION, even when they
  share no words.
  ANALOGY: Every sentence gets GPS coordinates on a "meaning map".
  "payment took too long to confirm" lands next to "bank timeout: response
  not received within the time window", so we can find it by distance.

CONCEPT — Sentence-Transformers:
  A Python library that wraps pre-trained transformer models (like BERT)
  and gives a single `.encode(text)` -> vector call. It runs locally;
  the model (~90 MB) downloads once on first use and is cached.

CONCEPT — Cosine similarity:
  Measures the angle between two vectors (1 = same direction/meaning).
  If vectors are normalised to length 1, cosine = a simple dot product.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.utils.logger import logger


class DenseIndex:
    def __init__(self, texts: list[str]):
        logger.info("Loading embedding model %s ...", settings.embed_model)
        self.model = SentenceTransformer(settings.embed_model)
        # Encode ALL chunks once at startup -> matrix of shape (num_chunks, 384).
        # normalize_embeddings=True makes every vector length 1 (for cosine).
        self.matrix = self.model.encode(texts, normalize_embeddings=True)

    def scores(self, query: str) -> list[float]:
        """Cosine similarity between the query and every chunk."""
        query_vec = self.model.encode([query], normalize_embeddings=True)[0]
        # Matrix (N x 384) @ vector (384) = N similarity scores in one step.
        return np.asarray(self.matrix @ query_vec, dtype=float).tolist()
