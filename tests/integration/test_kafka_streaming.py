
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Machine, TelemetryLog
from services.ingestion.consumer import TelemetryConsumer
from services.ingestion.producer import TelemetryProducer


@pytest.fixture
def db_session():
    """Provides an isolated in-memory SQLite database session for ingestion testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed test machines
    m1 = Machine(machine_code="M1000", machine_type="Heavy CNC Milling")
    m2 = Machine(machine_code="M1001", machine_type="Hydraulic Press")
    session.add_all([m1, m2])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_telemetry_producer_mock_send():
    """Verifies that TelemetryProducer correctly serializes and keys messages by machine_id."""
    producer = TelemetryProducer(mock_mode=True)

    telemetry_data = {
        "machine_id": "M1000",
        "temperature": 72.5,
        "vibration": 3.8,
        "pressure": 105.2,
        "rpm": 1800,
        "voltage": 380.0,
        "current": 12.4,
        "power": 4.7,
        "humidity": 45.0,
        "load": 80.0,
        "operating_hours": 120.5,
        "maintenance_count": 2,
        "failure": 0,
        "failure_type": "Healthy Baseline",
        "RUL": 42.0,
    }

    success = producer.send_telemetry(telemetry_data, topic="sensor-telemetry-raw")
    assert success is True
    assert producer.published_count == 1
    assert len(producer.mock_sent_records) == 1

    record = producer.mock_sent_records[0]
    assert record["topic"] == "sensor-telemetry-raw"
    assert record["key"] == "M1000"
    assert record["value"]["temperature"] == 72.5


def test_telemetry_producer_stream_csv(tmp_path):
    """Verifies that stream_csv_dataset reads a dataset and emits all rows."""
    csv_file = tmp_path / "test_sensors.csv"
    csv_file.write_text(
        "machine_id,temperature,vibration,pressure,rpm,voltage,current,power,humidity,load,operating_hours,maintenance_count,failure,failure_type,RUL\n"
        "M1000,65.0,1.2,100.0,1500,380.0,10.0,3.8,50.0,60.0,10.0,0,0,Healthy Baseline,50.0\n"
        "M1001,78.0,3.5,95.0,1750,385.0,11.5,4.4,48.0,75.0,25.0,1,0,Healthy Baseline,35.0\n"
    )

    producer = TelemetryProducer(mock_mode=True)
    count = producer.stream_csv_dataset(str(csv_file), rate_hz=0, max_records=2)

    assert count == 2
    assert producer.published_count == 2
    assert producer.mock_sent_records[0]["key"] == "M1000"
    assert producer.mock_sent_records[1]["key"] == "M1001"


def test_telemetry_consumer_record_processing(db_session):
    """Verifies that TelemetryConsumer converts JSON records into TelemetryLog instances."""
    consumer = TelemetryConsumer(mock_mode=True)

    raw_record = {
        "machine_id": "M1000",
        "timestamp": "2026-08-29T12:00:00",
        "temperature": 82.3,
        "vibration": 4.1,
        "pressure": 110.0,
        "rpm": 1900.0,
        "voltage": 390.0,
        "current": 14.2,
        "power": 5.5,
        "humidity": 40.0,
        "load": 92.0,
        "operating_hours": 300.0,
        "maintenance_count": 3,
        "failure": 1,
        "failure_type": "Bearing Wear",
        "RUL": 4.5,
    }

    log_entry = consumer.process_record(raw_record, db=db_session)
    assert log_entry is not None
    assert log_entry.temperature == 82.3
    assert log_entry.vibration == 4.1
    assert log_entry.failure == 1
    assert log_entry.failure_type == "Bearing Wear"
    assert log_entry.rul == 4.5


def test_telemetry_consumer_batch_persistence(db_session):
    """Verifies that save_batch correctly writes micro-batches to the database."""
    consumer = TelemetryConsumer(mock_mode=True)

    batch = [
        {
            "machine_id": "M1000",
            "temperature": 70.0,
            "vibration": 1.5,
            "pressure": 100.0,
            "rpm": 1500,
            "voltage": 380,
            "current": 10,
            "power": 3.8,
            "humidity": 50,
            "load": 60,
            "operating_hours": 50,
            "maintenance_count": 0,
            "failure": 0,
            "RUL": 48.0,
        },
        {
            "machine_id": "M1001",
            "temperature": 75.0,
            "vibration": 2.2,
            "pressure": 102.0,
            "rpm": 1600,
            "voltage": 382,
            "current": 11,
            "power": 4.2,
            "humidity": 48,
            "load": 70,
            "operating_hours": 80,
            "maintenance_count": 1,
            "failure": 0,
            "RUL": 40.0,
        },
    ]

    saved_count = consumer.save_batch(batch, db=db_session)
    assert saved_count == 2

    # Query DB to verify persistence
    logs = db_session.scalars(select(TelemetryLog)).all()
    assert len(logs) == 2
    assert logs[0].temperature == 70.0
    assert logs[1].temperature == 75.0
