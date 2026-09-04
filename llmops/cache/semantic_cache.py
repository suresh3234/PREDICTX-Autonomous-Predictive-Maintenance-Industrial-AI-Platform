import time
from typing import Any

import numpy as np

from rag.embeddings.embedder import CachedEmbedder


class SemanticCache:
    """
    Semantic Response Cache for Industrial LLM Copilot queries.
    Uses dense vector similarity to serve instant cached responses for semantically equivalent questions.
    """

    def __init__(self, embedder: CachedEmbedder | None = None, similarity_threshold: float = 0.95):
        self.embedder = embedder or CachedEmbedder()
        self.similarity_threshold = similarity_threshold
        self._cache_entries: list[dict[str, Any]] = []
        self._hits = 0
        self._misses = 0

    def get(self, query: str, threshold: float | None = None) -> dict[str, Any] | None:
        """
        Retrieves cached response if a semantically similar query is found.
        """
        if not self._cache_entries or not query.strip():
            self._misses += 1
            return None

        thresh = threshold or self.similarity_threshold
        q_emb = self.embedder.encode(query, normalize=True)

        best_score = -1.0
        best_entry = None

        for entry in self._cache_entries:
            sim = float(np.dot(q_emb, entry["embedding"]))
            if sim > best_score:
                best_score = sim
                best_entry = entry

        if best_score >= thresh and best_entry is not None:
            self._hits += 1
            return {
                "response": best_entry["response"],
                "similarity": round(best_score, 4),
                "cached_at": best_entry["timestamp"],
                "matched_query": best_entry["query"],
                "metadata": best_entry["metadata"],
            }

        self._misses += 1
        return None

    def set(self, query: str, response: str, metadata: dict[str, Any] | None = None):
        """
        Stores query, embedding vector, and response in the semantic cache.
        """
        if not query.strip() or not response.strip():
            return

        q_emb = self.embedder.encode(query, normalize=True)
        entry = {
            "query": query,
            "embedding": q_emb,
            "response": response,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self._cache_entries.append(entry)

    def clear(self):
        """Empties the semantic cache."""
        self._cache_entries.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Returns semantic cache efficiency telemetry."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        return {
            "cache_size": len(self._cache_entries),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
            "threshold": self.similarity_threshold,
        }
