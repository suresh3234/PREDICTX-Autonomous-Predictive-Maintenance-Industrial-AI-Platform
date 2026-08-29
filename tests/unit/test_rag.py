import json
import os

import pytest

from rag.vector_store import HybridRetriever


@pytest.fixture
def retriever_setup():
    retriever = HybridRetriever(model_name="all-MiniLM-L6-v2")

    # Load knowledge manuals
    manuals_path = "data/knowledge/manuals.json"
    assert os.path.exists(manuals_path)
    with open(manuals_path) as f:
        documents = json.load(f)

    retriever.index_documents(documents)
    return retriever


def test_semantic_vector_retrieval(retriever_setup):
    retriever = retriever_setup

    # Semantic search query (no exact word matches)
    query = "vibration squealing ball replacement shaft coupling grease"
    results = retriever.retrieve(
        query, top_k=2, alpha=1.0
    )  # alpha=1.0 checks pure vector search

    assert len(results) == 2
    assert results[0]["document_id"] == "man_bearing_wear"
    assert results[0]["score"] > 0.50


def test_lexical_keyword_retrieval(retriever_setup):
    retriever = retriever_setup

    # Keyword search query matching specific tokens
    query = "pressure gasket coupling retorque 120 Nm"
    results = retriever.retrieve(
        query, top_k=2, alpha=0.0
    )  # alpha=0.0 checks pure BM25 search

    assert len(results) == 2
    assert results[0]["document_id"] == "man_pressure_leak"
    assert results[0]["score"] > 0.50


def test_hybrid_fusion_retrieval(retriever_setup):
    retriever = retriever_setup

    query = "cooling fluid lines radiator fin temperature clogging fan"
    results = retriever.retrieve(
        query, top_k=3, alpha=0.5
    )  # alpha=0.5 checks hybrid fusion

    assert len(results) == 3
    # Check that score components are normalized in range [0, 1]
    for doc in results:
        assert 0.0 <= doc["dense_score"] <= 1.0
        assert 0.0 <= doc["sparse_score"] <= 1.0
        assert 0.0 <= doc["score"] <= 1.0
