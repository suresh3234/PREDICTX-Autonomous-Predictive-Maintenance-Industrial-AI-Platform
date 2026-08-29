from pathlib import Path
from typing import Any, Optional
from mcp.base import MCPServerBase
from rag.engine import AdvancedRAGEngine


class KnowledgeMCPServer(MCPServerBase):
    """
    MCP Server for Technical Manuals and Standard Operating Procedure (SOP) Retrieval.
    """

    def __init__(self, rag_engine: Optional[AdvancedRAGEngine] = None):
        super().__init__(name="predictx-knowledge-server", version="1.0.0")
        root = Path(__file__).resolve().parents[2]
        self.manuals_path = root / "data" / "knowledge" / "manuals.json"
        
        if rag_engine:
            self.rag_engine = rag_engine
        else:
            self.rag_engine = AdvancedRAGEngine()
            if self.manuals_path.exists():
                self.rag_engine.index_file_or_directory(self.manuals_path)

        self._register_knowledge_tools()

    def _register_knowledge_tools(self):
        @self.tool(
            name="search_manuals",
            description="Searches industrial maintenance manuals and reliability SOPs using hybrid semantic retrieval."
        )
        def search_manuals(query: str, top_k: int = 2) -> list[dict[str, Any]]:
            results = self.rag_engine.retrieve(query=query, top_k=top_k)
            return [
                {
                    "doc_id": r.get("document_id") or r.get("id"),
                    "text": r.get("text"),
                    "source": r.get("metadata", {}).get("source", "Manual"),
                    "score": r.get("rerank_score", r.get("score", 0.9)),
                }
                for r in results
            ]

        @self.tool(
            name="get_failure_sop",
            description="Retrieves the exact Standard Operating Procedure for a given equipment failure category (vibration, temperature, pressure, electrical)."
        )
        def get_failure_sop(failure_mode: str) -> dict[str, Any]:
            results = self.rag_engine.retrieve(query=f"{failure_mode} SOP repair procedure", top_k=1)
            if results:
                top = results[0]
                return {
                    "failure_mode": failure_mode,
                    "sop_id": top.get("document_id") or top.get("id"),
                    "procedure": top.get("text"),
                    "source": top.get("metadata", {}).get("source"),
                }
            return {"error": f"No SOP found for failure mode '{failure_mode}'."}
