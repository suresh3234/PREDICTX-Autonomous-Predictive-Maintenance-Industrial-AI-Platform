import hashlib

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class CachedEmbedder:
    """
    Dense text embedding engine with memory caching to accelerate inference.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.cache: dict[str, np.ndarray] = {}
        self.encoder = None

        if SentenceTransformer is not None:
            self.encoder = SentenceTransformer(model_name)

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def encode(self, texts: str | list[str], normalize: bool = True) -> np.ndarray:
        """
        Encodes a single text or list of texts into normalized embedding vectors.
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else texts

        # Separate cached from non-cached
        uncached_texts = []
        uncached_indices = []
        result_embeddings = [None] * len(text_list)

        for i, t in enumerate(text_list):
            h = self._hash_text(t)
            if h in self.cache:
                result_embeddings[i] = self.cache[h]
            else:
                uncached_texts.append(t)
                uncached_indices.append(i)

        # Compute embeddings for new texts
        if uncached_texts:
            if self.encoder is not None:
                new_embs = self.encoder.encode(uncached_texts, show_progress_bar=False)
            else:
                # Fallback mock embedding if library not loaded
                np.random.seed(42)
                new_embs = np.random.randn(len(uncached_texts), 384)

            for idx, text_str, emb in zip(
                uncached_indices, uncached_texts, new_embs, strict=False
            ):
                if normalize:
                    emb = emb / (np.linalg.norm(emb) + 1e-8)
                self.cache[self._hash_text(text_str)] = emb
                result_embeddings[idx] = emb

        embeddings = np.array(result_embeddings)
        return embeddings[0] if is_single else embeddings
