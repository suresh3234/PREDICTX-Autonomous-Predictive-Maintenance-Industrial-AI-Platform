import re
from typing import Any


class RecursiveChunker:
    """
    Context-aware recursive chunker with sliding token overlap.
    Preserves procedural continuity and enriches chunks with parent metadata.
    """

    def __init__(self, chunk_size: int = 150, chunk_overlap: int = 30):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_into_sentences(self, text: str) -> list[str]:
        # Split on period, exclamation, question mark followed by space or newline
        sentences = re.split(r'(?<=[.?!])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, text: str) -> list[str]:
        """
        Recursively splits text into chunks of roughly `chunk_size` words with `chunk_overlap`.
        """
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        step = max(self.chunk_size - self.chunk_overlap, 1)
        
        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            if i + self.chunk_size >= len(words):
                break

        return chunks

    def chunk_document(self, doc: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Chunks a document dict and propagates metadata with chunk tracking.
        """
        text = doc.get("text", "")
        doc_id = doc.get("id", "doc")
        base_meta = doc.get("metadata", {})

        text_chunks = self.chunk_text(text)
        total_chunks = len(text_chunks)

        result_chunks = []
        for idx, chunk_str in enumerate(text_chunks):
            result_chunks.append({
                "id": f"{doc_id}_c{idx+1}",
                "parent_id": doc_id,
                "text": chunk_str,
                "metadata": {
                    **base_meta,
                    "parent_document_id": doc_id,
                    "chunk_index": idx + 1,
                    "total_chunks": total_chunks,
                },
            })

        return result_chunks

    def chunk_documents(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Chunks a collection of documents."""
        all_chunks = []
        for d in documents:
            all_chunks.extend(self.chunk_document(d))
        return all_chunks
