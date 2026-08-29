import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Optional
import pandas as pd

try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
except ImportError:
    KafkaProducer = None
    KafkaError = None

logger = logging.getLogger("PredictX.KafkaProducer")


class TelemetryProducer:
    """
    High-throughput, partitioned Kafka Producer for industrial IoT sensor streams.
    Ensures chronological ordering per machine by partitioning on machine_id.
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "predictx-telemetry-producer",
        mock_mode: bool = False,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.mock_mode = mock_mode
        self.producer = None
        self.published_count = 0
        self.mock_sent_records: list[dict] = []

        if not self.mock_mode and KafkaProducer is not None:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    client_id=self.client_id,
                    key_serializer=lambda k: str(k).encode("utf-8") if k is not None else None,
                    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                    acks="all",  # Strong durability guarantee
                    retries=3,
                    linger_ms=10,  # Micro-batching latency
                    max_in_flight_requests_per_connection=1,  # Strict partition ordering
                )
                logger.info(f"Connected KafkaProducer to {self.bootstrap_servers}")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Kafka at {self.bootstrap_servers} ({e}). "
                    "Falling back to MOCK mode."
                )
                self.mock_mode = True
        else:
            self.mock_mode = True

    def send_telemetry(
        self,
        telemetry: dict[str, Any],
        topic: str = "sensor-telemetry-raw",
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> bool:
        """
        Sends a telemetry record keyed by machine_id.
        """
        machine_id = telemetry.get("machine_id", telemetry.get("machine_code", "UNKNOWN"))

        if self.mock_mode or self.producer is None:
            self.mock_sent_records.append({
                "topic": topic,
                "key": machine_id,
                "value": telemetry,
                "timestamp": time.time(),
            })
            self.published_count += 1
            if on_success:
                on_success({"status": "MOCK_SENT", "topic": topic, "key": machine_id})
            return True

        try:
            future = self.producer.send(
                topic=topic,
                key=machine_id,
                value=telemetry,
            )
            if on_success:
                future.add_callback(on_success)
            if on_error:
                future.add_errback(on_error)

            self.published_count += 1
            return True
        except Exception as e:
            logger.error(f"Error publishing telemetry for {machine_id} to {topic}: {e}")
            if on_error:
                on_error(e)
            return False

    def flush(self, timeout: float = 5.0):
        """Flushes buffered records to the Kafka broker."""
        if self.producer and not self.mock_mode:
            self.producer.flush(timeout=timeout)

    def close(self):
        """Closes producer connection."""
        if self.producer and not self.mock_mode:
            self.producer.flush()
            self.producer.close()
            logger.info("KafkaProducer connection closed.")

    def stream_csv_dataset(
        self,
        csv_path: str,
        topic: str = "sensor-telemetry-raw",
        rate_hz: float = 10.0,
        max_records: Optional[int] = None,
    ) -> int:
        """
        Streams records from a historical CSV dataset into Kafka at a specified frequency.
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"Sensor CSV not found at {csv_path}")

        df = pd.read_csv(path)
        if max_records:
            df = df.head(max_records)

        records = df.to_dict(orient="records")
        delay = 1.0 / rate_hz if rate_hz > 0 else 0

        sent = 0
        for row in records:
            # Format row dictionary
            self.send_telemetry(row, topic=topic)
            sent += 1
            if delay > 0:
                time.sleep(delay)

        self.flush()
        return sent
