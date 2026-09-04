from rag.chunking.chunker import RecursiveChunker
from rag.embeddings.embedder import CachedEmbedder
from rag.engine import AdvancedRAGEngine
from rag.parsing.parser import DocumentParser
from rag.reranking.reranker import CrossEncoderReranker
from rag.retrieval.query_expander import QueryExpander


def test_document_parser_markdown():
    md_content = """# Section 1: Vibration Analysis
Abnormal vibration indicates bearing defect or misalignment.

## Section 2: Thermal Maintenance
Inspect coolant radiator lines for clogging."""

    docs = DocumentParser.parse_markdown(md_content, source_name="test_manual.md")
    assert len(docs) == 2
    assert "Section 1: Vibration Analysis" in docs[0]["text"]
    assert docs[0]["metadata"]["heading_level"] == 1
    assert "Section 2: Thermal Maintenance" in docs[1]["text"]
    assert docs[1]["metadata"]["heading_level"] == 2


def test_recursive_chunker():
    chunker = RecursiveChunker(chunk_size=10, chunk_overlap=3)
    text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12 Word13 Word14 Word15"

    doc = {"id": "test_doc", "text": text, "metadata": {"category": "test"}}
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 1
    assert chunks[0]["metadata"]["parent_document_id"] == "test_doc"
    assert chunks[0]["metadata"]["chunk_index"] == 1
    assert chunks[0]["metadata"]["category"] == "test"


def test_cached_embedder():
    embedder = CachedEmbedder()
    text = "Predictive maintenance vibration analysis"

    # First call generates embedding
    emb1 = embedder.encode(text)
    assert emb1 is not None
    assert len(embedder.cache) == 1

    # Second call fetches from cache
    emb2 = embedder.encode(text)
    assert (emb1 == emb2).all()


def test_query_expander():
    expander = QueryExpander()
    query = "Machine is shaking violently and running hot"
    expanded = expander.expand(query)

    assert "vibration" in expanded
    assert "bearing wear" in expanded
    assert "overheating" in expanded or "thermal" in expanded


def test_cross_encoder_reranker():
    reranker = CrossEncoderReranker(mock_mode=True)
    query = "bearing wear vibration"
    candidates = [
        {"id": "doc_1", "text": "Electrical wiring insulation check with megohmmeter", "score": 0.8},
        {"id": "doc_2", "text": "High vibration indicates critical bearing wear and defect", "score": 0.4},
    ]

    results = reranker.rerank(query, candidates, top_n=2)
    # The bearing doc should be reranked to rank 1 due to high relevance overlap
    assert results[0]["id"] == "doc_2"
    assert results[0]["rank"] == 1


def test_advanced_rag_engine_end_to_end(tmp_path):
    manual_file = tmp_path / "manuals.json"
    manual_file.write_text("""[
        {
            "id": "man_bearing",
            "text": "Bearing wear troubleshooting: High vibration above 3.5 mm/s requires immediate bearing replacement and lubrication.",
            "metadata": {"category": "vibration"}
        },
        {
            "id": "man_hydraulic",
            "text": "Hydraulic pressure drops below 80 PSI indicate seal leakage in pressure chamber.",
            "metadata": {"category": "pressure"}
        }
    ]""")

    engine = AdvancedRAGEngine()
    indexed_count = engine.index_file_or_directory(manual_file)
    assert indexed_count >= 2

    # Query with informal vocabulary
    results = engine.retrieve("Why is the equipment shaking?", top_k=1)
    assert len(results) == 1
    assert "man_bearing" in results[0]["document_id"]
