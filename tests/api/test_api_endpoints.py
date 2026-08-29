import sys
from pathlib import Path
from datetime import datetime

# Add root directory to sys.path programmatically
ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))
# Add apps/api to path as well
if str(ROOT_PATH / "apps" / "api") not in sys.path:
    sys.path.insert(0, str(ROOT_PATH / "apps" / "api"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base
from app.db.session import get_db
from app.db.models import Machine, TelemetryLog

# Setup memory SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed a machine and its telemetry
    mach = Machine(machine_code="M1000", machine_type="Medium Duty")
    db.add(mach)
    db.commit()
    db.refresh(mach)

    log = TelemetryLog(
        machine_id=mach.id,
        timestamp=datetime.utcnow(),
        temperature=65.2,
        vibration=1.8,
        pressure=105.0,
        rpm=1520.0,
        voltage=221.0,
        current=10.5,
        power=2.3,
        humidity=51.0,
        load=72.0,
        operating_hours=125.5,
        maintenance_count=1,
        last_maintenance=datetime.utcnow(),
        failure=0,
        failure_type="None",
        rul=42.0
    )
    db.add(log)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_list_machines():
    res = client.get("/api/v1/machines")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["items"][0]["machine_code"] == "M1000"


def test_create_machine():
    payload = {"machine_code": "M9999", "machine_type": "Light Industrial"}
    res = client.post("/api/v1/machines", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["machine_code"] == "M9999"
    assert data["machine_type"] == "Light Industrial"
    assert "id" in data


def test_get_machine_predictions():
    res = client.get("/api/v1/predictions/M1000")
    assert res.status_code == 200
    data = res.json()
    assert data["machine_code"] == "M1000"
    assert "telemetry" in data
    assert "predictions" in data
    predictions = data["predictions"]
    assert "anomaly_severity" in predictions
    assert "failure_probability" in predictions
    assert "predicted_rul" in predictions


def test_get_machine_predictions_not_found():
    res = client.get("/api/v1/predictions/M8888")
    assert res.status_code == 404


def test_query_copilot():
    payload = {"query": "Is machine M1000 healthy?"}
    res = client.post("/api/v1/copilot/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["machine_id"] == "M1000"
    assert "telemetry" in data
    assert "predictions" in data
    assert "answer" in data
    assert "retrieved_documents" in data


def test_trigger_retraining():
    payload = {"task": "anomaly_detection", "force": True}
    res = client.post("/api/v1/retrain", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["retrained"] is True
    assert "promoted" in data
    assert "version" in data
