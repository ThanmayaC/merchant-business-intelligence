"""
bm25.py — KEYWORD search (written by hand so you can see how it works).

CONCEPT — BM25 ("Best Match 25"):
  It scores each chunk by how well its WORDS match the query words.
  ANALOGY: Searching a book's index. "BANK_TIMEOUT" appears on page 2?
  That page wins. It is great for exact codes and names, but it doesn't
  understand meaning ("slow confirmation" will not match "timeout").

  Three ideas inside the formula:
   1. TF  (term frequency): a word appearing more in a chunk -> higher score,
          but with diminishing returns (controlled by k1).
   2. IDF (inverse document frequency): RARE words count more.
          "the" is everywhere (worthless); "bank_timeout" is rare (valuable).
   3. Length normalisation: a long chunk naturally contains more words,
          so we don't let it win just for being long (controlled by b).
"""

import math
from collections import Counter

from app.utils.text import tokenize


class BM25Index:
    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        # Tokenize every chunk once, up front.
        self.docs = [tokenize(t) for t in texts]
        self.doc_lens = [len(d) for d in self.docs]
        self.avg_len = sum(self.doc_lens) / len(self.docs) if self.docs else 0.0
        # Word counts per chunk, e.g. {"bank": 2, "timeout": 1, ...}
        self.term_freqs = [Counter(d) for d in self.docs]

        # How many chunks contain each word (document frequency).
        doc_freq = Counter()
        for d in self.docs:
            doc_freq.update(set(d))

        # IDF: rare word -> big number, common word -> small number.
        n = len(self.docs)
        self.idf = {
            word: math.log(1 + (n - df + 0.5) / (df + 0.5)) for word, df in doc_freq.items()
        }

    def scores(self, query: str) -> list[float]:
        """Return one BM25 score per chunk (same order as `texts`)."""
        query_terms = tokenize(query)
        results = []
        for tf, length in zip(self.term_freqs, self.doc_lens):
            score = 0.0
            for term in query_terms:
                if term not in tf:
                    continue
                f = tf[term]
                # The BM25 formula: IDF * (saturated TF with length normalisation)
                numerator = f * (self.k1 + 1)
                denominator = f + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                score += self.idf[term] * numerator / denominator
            results.append(score)
        return results
