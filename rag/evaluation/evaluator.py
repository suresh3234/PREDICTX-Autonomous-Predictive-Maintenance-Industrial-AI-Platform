import re
from typing import Any

import numpy as np

from rag.embeddings.embedder import CachedEmbedder


class RAGEvaluator:
    """
    RAG Triad Evaluation Engine.
    Quantitatively scores RAG outputs across:
    1. Context Relevance (Retrieval Precision)
    2. Groundedness / Faithfulness (Anti-Hallucination)
    3. Answer Relevance (Intent Fulfillment)
    """

    def __init__(self, embedder: CachedEmbedder | None = None):
        self.embedder = embedder or CachedEmbedder()

    def _split_into_claims(self, text: str) -> list[str]:
        """Splits an answer into discrete factual claims / sentences."""
        # Split on sentence boundaries and bullet points
        raw_lines = re.split(r'(?<=[.?!])\s+|\n[-*•]\s+|\n\d+\.\s+', text)
        claims = [c.strip() for c in raw_lines if len(c.strip()) > 10]
        return claims if claims else [text.strip()]

    def _match_word(self, word: str, word_set: set[str]) -> bool:
        """Checks exact or stem/prefix match (e.g. bearing/bearings, replace/replacement)."""
        if word in word_set:
            return True
        stem = word[:4] if len(word) >= 5 else word
        return any(w.startswith(stem) or stem in w for w in word_set)

    def evaluate_context_relevance(self, query: str, contexts: list[str | dict[str, Any]]) -> float:
        """
        Measures the degree to which retrieved contexts are relevant to the query.
        Returns a score in [0.0, 1.0].
        """
        if not contexts:
            return 0.0

        context_texts = [c if isinstance(c, str) else c.get("text", "") for c in contexts]
        combined_context = " ".join(context_texts)

        # 1. Lexical keyword overlap with stem/inflection support
        stopwords = {"how", "the", "what", "and", "for", "with", "that", "this", "from", "are", "was", "were", "when", "why", "high"}
        query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())) - stopwords
        context_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', combined_context.lower()))

        if not query_words:
            overlap_score = 0.5
        else:
            matches = sum(1 for qw in query_words if self._match_word(qw, context_words))
            overlap_score = matches / len(query_words)

        # 2. Semantic Embedding Similarity
        q_emb = self.embedder.encode(query, normalize=True)
        c_emb = self.embedder.encode(combined_context[:1000], normalize=True)
        cos_sim = float(np.dot(q_emb, c_emb))
        semantic_score = max(0.0, min(cos_sim, 1.0))

        # Balanced combination
        score = 0.5 * min(overlap_score, 1.0) + 0.5 * semantic_score
        return round(float(score), 4)

    def evaluate_faithfulness(self, answer: str, contexts: list[str | dict[str, Any]]) -> float:
        """
        Measures the proportion of claims in the generated answer that are supported
        by the retrieved context (Hallucination Detection).
        Returns a score in [0.0, 1.0].
        """
        if not answer.strip():
            return 0.0
        if not contexts:
            return 0.0

        context_texts = [c if isinstance(c, str) else c.get("text", "") for c in contexts]
        full_context = " ".join(context_texts).lower()

        claims = self._split_into_claims(answer)
        if not claims:
            return 1.0

        supported_count = 0
        for claim in claims:
            claim_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', claim.lower()))
            stopwords = {"the", "and", "that", "this", "with", "from", "for", "are", "was", "were", "machine", "when", "using"}
            meaningful_words = claim_words - stopwords

            if not meaningful_words:
                supported_count += 1
                continue

            matched = sum(1 for w in meaningful_words if w in full_context or (len(w) >= 4 and w[:4] in full_context))
            match_ratio = matched / len(meaningful_words)

            if match_ratio >= 0.40:
                supported_count += 1

        faithfulness = supported_count / len(claims)
        return round(float(min(faithfulness, 1.0)), 4)

    def evaluate_answer_relevance(self, query: str, answer: str) -> float:
        """
        Measures how directly the generated answer addresses the user query.
        Returns a score in [0.0, 1.0].
        """
        if not answer.strip() or not query.strip():
            return 0.0

        # Semantic cosine similarity
        q_emb = self.embedder.encode(query, normalize=True)
        a_emb = self.embedder.encode(answer, normalize=True)
        cos_sim = float(np.dot(q_emb, a_emb))

        stopwords = {"what", "the", "for", "how", "and", "with", "is", "are"}
        q_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())) - stopwords
        a_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', answer.lower()))

        if not q_words:
            overlap = 0.5
        else:
            matches = sum(1 for qw in q_words if self._match_word(qw, a_words))
            overlap = matches / len(q_words)

        relevance = 0.5 * max(0.0, min(cos_sim, 1.0)) + 0.5 * min(overlap, 1.0)
        return round(float(min(relevance, 1.0)), 4)

    def evaluate_rag_triad(
        self, query: str, contexts: list[str | dict[str, Any]], answer: str
    ) -> dict[str, Any]:
        """
        Computes the complete RAG Triad score card.
        """
        ctx_rel = self.evaluate_context_relevance(query, contexts)
        faith = self.evaluate_faithfulness(answer, contexts)
        ans_rel = self.evaluate_answer_relevance(query, answer)

        # Composite RAG Quality Index (Geometric mean style harmonic balance)
        composite = (ctx_rel * 0.35) + (faith * 0.35) + (ans_rel * 0.30)

        # Quality tier
        if composite >= 0.70:
            status = "PASSED (High Fidelity)"
        elif composite >= 0.50:
            status = "ACCEPTABLE"
        else:
            status = "FLAGGED (Potential Hallucination/Irrelevance)"

        return {
            "context_relevance": ctx_rel,
            "faithfulness": faith,
            "answer_relevance": ans_rel,
            "composite_score": round(composite, 4),
            "status": status,
        }
