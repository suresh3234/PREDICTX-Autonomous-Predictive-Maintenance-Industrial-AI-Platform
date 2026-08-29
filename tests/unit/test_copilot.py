import pandas as pd
import pytest

from agents.copilot import AgenticCopilot
from ml.registry.manager import ModelRegistryManager
from rag.generator import RAGGenerator
from rag.vector_store import HybridRetriever


@pytest.fixture
def copilot_setup(tmp_path):
    # 1. Create mock sensor log CSV
    sensor_path = tmp_path / "sensor_logs.csv"
    data = {
        "machine_id": ["M1000", "M1000", "M2000"],
        "timestamp": [
            "2026-08-01 10:00:00",
            "2026-08-01 10:10:00",
            "2026-08-01 10:00:00",
        ],
        "temperature": [45.0, 52.0, 38.0],
        "vibration": [1.2, 3.8, 1.0],
        "pressure": [100.0, 95.0, 102.0],
        "rpm": [1500.0, 1480.0, 1500.0],
        "voltage": [220.0, 220.0, 220.0],
        "current": [10.0, 12.0, 9.8],
        "power": [2.2, 2.6, 2.1],
        "humidity": [50.0, 50.0, 50.0],
        "load": [70.0, 80.0, 65.0],
        "operating_hours": [120.0, 120.1, 80.0],
        "maintenance_count": [1, 1, 0],
        "last_maintenance": ["2026-07-15", "2026-07-15", "2026-08-01"],
        "failure": [0, 0, 0],
        "failure_type": ["None", "None", "None"],
        "RUL": [45.0, 42.0, 80.0],
    }
    pd.DataFrame(data).to_csv(sensor_path, index=False)

    # 2. Setup mock registry and retriever
    registry = ModelRegistryManager(str(tmp_path / "store"))
    retriever = HybridRetriever()
    manuals = [
        {
            "id": "man_bearing",
            "text": "vibration wear troubleshooting guide. replace bearings.",
            "metadata": {"source": "manual"},
        }
    ]
    retriever.index_documents(manuals)
    generator = RAGGenerator(retriever, api_key=None)

    copilot = AgenticCopilot(
        registry_manager=registry,
        rag_generator=generator,
        sensor_data_path=str(sensor_path),
    )
    return copilot


def test_machine_id_extraction(copilot_setup):
    copilot = copilot_setup
    assert copilot._extract_machine_id("Please check machine M1000 health") == "M1000"
    assert copilot._extract_machine_id("Health details of M_2000") == "M_2000"
    assert copilot._extract_machine_id("What is the temperature of m1000?") == "M1000"
    assert copilot._extract_machine_id("General questions about pumps") is None


def test_get_latest_telemetry(copilot_setup):
    copilot = copilot_setup
    telemetry = copilot.get_latest_telemetry("M1000")
    # Assert it grabbed the latest timestamp (vibration 3.8, temp 52.0)
    assert telemetry["vibration"] == 3.8
    assert telemetry["temperature"] == 52.0

    with pytest.raises(ValueError):
        copilot.get_latest_telemetry("M9999")


def test_full_copilot_query_workflow(copilot_setup):
    copilot = copilot_setup
    res = copilot.query("M1000 is showing abnormal vibration")

    assert res["machine_id"] == "M1000"
    assert res["telemetry"]["temperature"] == 52.0
    assert "predictions" in res
    assert "man_bearing" in res["retrieved_documents"]
    assert "Maintenance Troubleshooting Advisory" in res["answer"]
