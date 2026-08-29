import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class HybridRetriever:
    """
    Custom Hybrid Search Retriever combining dense vector embeddings (SentenceTransformers)
    with sparse lexical keyword retrieval (BM25Okapi) from scratch.
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"Initializing dense embedding model: {model_name}...")
        self.encoder = SentenceTransformer(model_name)
        self.documents = []
        self.doc_embeddings = None
        self.bm25 = None

    def _tokenize(self, text: str) -> list[str]:
        # Simple tokenization: lowercase, split, strip punctuation
        return [
            word.strip(".,?!;:()\"'").lower() for word in text.split() if word.strip()
        ]

    def index_documents(self, documents: list[dict]):
        """
        Indexes a list of documents.
        Each document is a dict: {"id": str, "text": str, "metadata": dict}
        """
        if not documents:
            raise ValueError("Document list cannot be empty.")

        self.documents = documents
        texts = [doc["text"] for doc in documents]

        # 1. Compute Dense Vector Embeddings
        print("Generating dense vector embeddings for indexed corpus...")
        self.doc_embeddings = self.encoder.encode(texts, show_progress_bar=False)
        # Normalize embeddings for easy cosine similarity computation
        norms = np.linalg.norm(self.doc_embeddings, axis=1, keepdims=True)
        self.doc_embeddings = self.doc_embeddings / (norms + 1e-8)

        # 2. Fit Sparse Lexical BM25
        print("Fitting lexical BM25 index on tokenized corpus...")
        tokenized_corpus = [self._tokenize(t) for t in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"Successfully indexed {len(documents)} documents.")
        return self

    def retrieve(self, query: str, top_k: int = 3, alpha: float = 0.5) -> list[dict]:
        """
        Performs Hybrid Search using normalized scores.
        Score = alpha * normalized_vector_score + (1 - alpha) * normalized_bm25_score
        """
        if not self.documents:
            raise RuntimeError("Retriever is empty. Index documents before querying.")

        # 1. Dense Semantic Score (Cosine Similarity)
        query_emb = self.encoder.encode([query], show_progress_bar=False)[0]
        query_emb_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)

        # Cosine similarity since both doc and query embeddings are normalized
        vector_sims = np.dot(self.doc_embeddings, query_emb_norm)

        # Normalize vector scores to [0, 1] range
        v_min, v_max = vector_sims.min(), vector_sims.max()
        if v_max - v_min > 1e-8:
            vector_scores = (vector_sims - v_min) / (v_max - v_min)
        else:
            vector_scores = np.zeros_like(vector_sims)

        # 2. Sparse Keyword Score (BM25)
        tokenized_query = self._tokenize(query)
        bm25_raw_scores = np.array(self.bm25.get_scores(tokenized_query))

        # Normalize BM25 scores to [0, 1] range
        b_min, b_max = bm25_raw_scores.min(), bm25_raw_scores.max()
        if b_max - b_min > 1e-8:
            keyword_scores = (bm25_raw_scores - b_min) / (b_max - b_min)
        else:
            keyword_scores = np.zeros_like(bm25_raw_scores)

        # 3. Hybrid Fusion
        combined_scores = alpha * vector_scores + (1 - alpha) * keyword_scores

        # Sort indices descending
        ranked_indices = np.argsort(combined_scores)[::-1]

        results = []
        for rank, idx in enumerate(ranked_indices[:top_k]):
            results.append(
                {
                    "rank": rank + 1,
                    "document_id": self.documents[idx]["id"],
                    "text": self.documents[idx]["text"],
                    "metadata": self.documents[idx]["metadata"],
                    "score": float(combined_scores[idx]),
                    "dense_score": float(vector_scores[idx]),
                    "sparse_score": float(keyword_scores[idx]),
                }
            )

        return results
