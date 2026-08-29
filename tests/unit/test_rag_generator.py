import pytest

from rag.generator import RAGGenerator
from rag.vector_store import HybridRetriever


@pytest.fixture
def rag_setup():
    # 1. Initialize retriever and index documents
    retriever = HybridRetriever()
    manuals = [
        {
            "id": "man_bearing",
            "text": "Bearing replacement guide: replace bearing when vibration exceeds 3.5 mm/s.",
            "metadata": {"source": "Mech-Guide"},
        }
    ]
    retriever.index_documents(manuals)

    # 2. Instantiate generator in mock mode
    generator = RAGGenerator(retriever=retriever, api_key=None)
    return generator


def test_rag_mock_generation(rag_setup):
    generator = rag_setup

    # Telemetry and predictions input
    telemetry = {"temperature": 65.0, "vibration": 4.2}
    predictions = {
        "anomaly_severity": "CRITICAL",
        "failure_type": "Bearing Failure",
        "predicted_rul": 4.8,
    }

    res = generator.generate_response(
        query="vibration is high squealing bearing",
        telemetry=telemetry,
        predictions=predictions,
    )

    assert res["query"] == "vibration is high squealing bearing"
    assert res["is_mock"] is True
    assert "man_bearing" in res["retrieved_documents"]

    # Check that mock text contains correct parameters and is structured
    assert "CRITICAL" in res["response"]
    assert "4.8 hours" in res["response"]
    assert "Bearing Failure" in res["response"]
    assert "🛠️ Maintenance Troubleshooting Advisory" in res["response"]
