import logging
from pathlib import Path
from typing import Any, Optional, Union

from rag.chunking.chunker import RecursiveChunker
from rag.parsing.parser import DocumentParser
from rag.reranking.reranker import CrossEncoderReranker
from rag.retrieval.query_expander import QueryExpander
from rag.vector_store import HybridRetriever

logger = logging.getLogger("PredictX.AdvancedRAG")


class AdvancedRAGEngine:
    """
    Unified Advanced RAG Engine for industrial predictive maintenance knowledge bases.
    Integrates multi-format parsing, recursive chunking, domain query expansion,
    hybrid dense/sparse retrieval, and neural cross-encoder reranking.
    """

    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        chunker: Optional[RecursiveChunker] = None,
        query_expander: Optional[QueryExpander] = None,
        reranker: Optional[CrossEncoderReranker] = None,
    ):
        self.retriever = retriever or HybridRetriever()
        self.chunker = chunker or RecursiveChunker(chunk_size=150, chunk_overlap=30)
        self.query_expander = query_expander or QueryExpander()
        self.reranker = reranker or CrossEncoderReranker()
        self.indexed_chunks: list[dict[str, Any]] = []

    def index_documents(self, documents: list[dict[str, Any]]):
        """
        Chunks and indexes raw document objects into the hybrid vector store.
        """
        logger.info(f"Ingesting {len(documents)} source documents...")
        chunks = self.chunker.chunk_documents(documents)
        self.indexed_chunks = chunks
        self.retriever.index_documents(chunks)
        logger.info(f"Successfully indexed {len(chunks)} contextual chunks.")
        return len(chunks)

    def index_file_or_directory(self, path_str: Union[str, Path]) -> int:
        """
        Parses all manual files in a directory or a single file and indexes them.
        """
        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path_str}")

        raw_docs = []
        if path.is_file():
            raw_docs.extend(DocumentParser.parse_file(path))
        elif path.is_dir():
            for ext in ["*.json", "*.md", "*.txt"]:
                for file_path in path.glob(ext):
                    raw_docs.extend(DocumentParser.parse_file(file_path))

        return self.index_documents(raw_docs)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        candidate_pool_size: int = 10,
        expand_query: bool = True,
        rerank: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Full 2-stage Advanced RAG retrieval:
        1. Query Expansion (Domain Synonyms)
        2. Stage 1: Fast Hybrid Dense + Sparse Search
        3. Stage 2: Cross-Encoder Neural Reranking
        """
        search_query = self.query_expander.expand(query) if expand_query else query
        logger.info(f"Advanced RAG Query: '{query}' -> Expanded: '{search_query}'")

        # Stage 1: Candidate Generation
        candidates = self.retriever.retrieve(
            query=search_query,
            top_k=max(candidate_pool_size, top_k),
        )

        # Stage 2: Neural Reranking
        if rerank and len(candidates) > 1:
            final_results = self.reranker.rerank(
                query=query,
                documents=candidates,
                top_n=top_k,
            )
        else:
            final_results = candidates[:top_k]

        return final_results
