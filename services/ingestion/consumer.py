import json
import logging
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
except ImportError:
    KafkaConsumer = None
    KafkaError = None

from app.db.models import Machine, TelemetryLog
from app.db.session import SessionLocal

logger = logging.getLogger("PredictX.KafkaConsumer")


class TelemetryConsumer:
    """
    Kafka Consumer with micro-batching and database persistence.
    Consumes sensor streams, checks operational thresholds, and writes records to PostgreSQL.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "predictx-telemetry-group",
        topic: str = "sensor-telemetry-raw",
        anomaly_topic: str = "sensor-anomalies",
        batch_size: int = 50,
        batch_timeout_sec: float = 1.0,
        mock_mode: bool = False,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic
        self.anomaly_topic = anomaly_topic
        self.batch_size = batch_size
        self.batch_timeout_sec = batch_timeout_sec
        self.mock_mode = mock_mode
        self.running = False
        self.consumer = None

        # Machine code -> DB id cache
        self.machine_cache: dict[str, int] = {}

        if not self.mock_mode and KafkaConsumer is not None:
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    key_deserializer=lambda k: k.decode("utf-8") if k else None,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else None,
                    consumer_timeout_ms=1000,  # Poll timeout
                )
                logger.info(f"Connected KafkaConsumer to {self.bootstrap_servers} (Group: {self.group_id})")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Kafka at {self.bootstrap_servers} ({e}). "
                    "Running in MOCK / MANUAL mode."
                )
                self.mock_mode = True
        else:
            self.mock_mode = True

    def _get_machine_id(self, db: Session, machine_code: str) -> int | None:
        """Resolves machine_code to database machine ID with local caching."""
        if machine_code in self.machine_cache:
            return self.machine_cache[machine_code]

        machine = db.scalar(select(Machine).where(Machine.machine_code == machine_code))
        if machine:
            self.machine_cache[machine_code] = machine.id
            return machine.id
        return None

    def process_record(self, raw_record: dict[str, Any], db: Session) -> TelemetryLog | None:
        """
        Parses and validates a single telemetry record into a database model instance.
        """
        code = raw_record.get("machine_id") or raw_record.get("machine_code", "M1000")
        mach_id = self._get_machine_id(db, code)
        if not mach_id:
            logger.warning(f"Skipping record for unknown machine: {code}")
            return None

        # Parse timestamp
        raw_ts = raw_record.get("timestamp")
        if isinstance(raw_ts, str):
            try:
                ts = datetime.fromisoformat(raw_ts.replace("Z", ""))
            except ValueError:
                ts = datetime.utcnow()
        elif isinstance(raw_ts, datetime):
            ts = raw_ts
        else:
            ts = datetime.utcnow()

        # Parse last maintenance
        raw_lm = raw_record.get("last_maintenance")
        if isinstance(raw_lm, str) and raw_lm:
            try:
                lm = datetime.fromisoformat(raw_lm.replace("Z", ""))
            except ValueError:
                lm = None
        else:
            lm = None

        log_entry = TelemetryLog(
            machine_id=mach_id,
            timestamp=ts,
            temperature=float(raw_record.get("temperature", 0.0)),
            vibration=float(raw_record.get("vibration", 0.0)),
            pressure=float(raw_record.get("pressure", 0.0)),
            rpm=float(raw_record.get("rpm", 0.0)),
            voltage=float(raw_record.get("voltage", 0.0)),
            current=float(raw_record.get("current", 0.0)),
            power=float(raw_record.get("power", 0.0)),
            humidity=float(raw_record.get("humidity", 0.0)),
            load=float(raw_record.get("load", 0.0)),
            operating_hours=float(raw_record.get("operating_hours", 0.0)),
            maintenance_count=int(raw_record.get("maintenance_count", 0)),
            last_maintenance=lm,
            failure=int(raw_record.get("failure", 0)),
            failure_type=str(raw_record.get("failure_type") or "None"),
            rul=float(raw_record.get("RUL", raw_record.get("rul", 0.0))),
        )
        return log_entry

    def save_batch(self, records: list[dict[str, Any]], db: Session | None = None) -> int:
        """
        Persists a batch of telemetry records to the database.
        """
        if not records:
            return 0

        session_created = False
        if db is None:
            db = SessionLocal()
            session_created = True

        try:
            log_entries = []
            for r in records:
                entry = self.process_record(r, db)
                if entry:
                    log_entries.append(entry)

            if log_entries:
                db.add_all(log_entries)
                db.commit()
                logger.info(f"Persisted micro-batch of {len(log_entries)} telemetry logs to database.")
            return len(log_entries)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist batch of telemetry logs: {e}")
            raise
        finally:
            if session_created:
                db.close()

    def consume_loop(self, max_batches: int | None = None, on_record_callback: Callable | None = None):
        """
        Main streaming loop with micro-batch flushing.
        """
        if self.mock_mode or self.consumer is None:
            logger.info("KafkaConsumer in MOCK mode. consume_loop exited.")
            return

        self.running = True
        batch: list[dict[str, Any]] = []
        last_flush = time.time()
        batches_processed = 0

        logger.info(f"Starting telemetry consumption loop on topic '{self.topic}'...")

        try:
            while self.running:
                # Poll message batch
                msg_pack = self.consumer.poll(timeout_ms=500, max_records=self.batch_size)
                now = time.time()

                for _tp, messages in msg_pack.items():
                    for msg in messages:
                        if msg.value:
                            batch.append(msg.value)
                            if on_record_callback:
                                on_record_callback(msg.value)

                # Flush condition: reached batch size or timeout elapsed
                if len(batch) >= self.batch_size or (batch and (now - last_flush) >= self.batch_timeout_sec):
                    self.save_batch(batch)
                    batch = []
                    last_flush = now
                    batches_processed += 1

                    if max_batches and batches_processed >= max_batches:
                        break

        except KeyboardInterrupt:
            logger.info("Consumer loop interrupted.")
        finally:
            if batch:
                self.save_batch(batch)
            self.close()

    def close(self):
        """Closes consumer connection."""
        self.running = False
        if self.consumer and not self.mock_mode:
            self.consumer.close()
            logger.info("KafkaConsumer connection closed.")
