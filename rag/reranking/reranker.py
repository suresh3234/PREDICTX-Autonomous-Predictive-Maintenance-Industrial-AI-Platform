from typing import Any

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None


class CrossEncoderReranker:
    """
    Stage-2 Neural Reranker using Cross-Encoder architectures.
    Computes deep query-document cross-attention scores to refine hybrid search results.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", mock_mode: bool = False):
        self.model_name = model_name
        self.mock_mode = mock_mode
        self.model = None

        if not self.mock_mode and CrossEncoder is not None:
            try:
                self.model = CrossEncoder(model_name)
            except Exception:
                self.mock_mode = True
        else:
            self.mock_mode = True

    def rerank(self, query: str, documents: list[dict[str, Any]], top_n: int = 3) -> list[dict[str, Any]]:
        """
        Reranks a list of candidate documents against the query.
        """
        if not documents:
            return []

        if len(documents) <= 1:
            return documents[:top_n]

        if not self.mock_mode and self.model is not None:
            pairs = [[query, doc["text"]] for doc in documents]
            scores = self.model.predict(pairs)
        else:
            # High-precision keyword overlap + Stage 1 dense score fusion for mock mode
            scores = []
            query_words = set(query.lower().split())
            for doc in documents:
                doc_words = set(doc["text"].lower().split())
                overlap = len(query_words.intersection(doc_words)) / (len(query_words) + 1e-6)
                prior_score = doc.get("score", 0.5)
                scores.append(0.6 * overlap + 0.4 * prior_score)

        # Attach rerank score and sort
        reranked_docs = []
        for doc, score in zip(documents, scores, strict=False):
            doc_copy = dict(doc)
            doc_copy["rerank_score"] = float(score)
            reranked_docs.append(doc_copy)

        reranked_docs.sort(key=lambda d: d["rerank_score"], reverse=True)

        # Update ranks
        for idx, d in enumerate(reranked_docs[:top_n]):
            d["rank"] = idx + 1

        return reranked_docs[:top_n]
