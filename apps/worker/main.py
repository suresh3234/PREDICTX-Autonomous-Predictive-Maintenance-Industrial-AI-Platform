import logging
import signal
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))
if str(ROOT_PATH / "apps" / "api") not in sys.path:
    sys.path.insert(0, str(ROOT_PATH / "apps" / "api"))

from app.core.config import settings
from services.ingestion.consumer import TelemetryConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("PredictX.Worker")


def main():
    logger.info("Initializing PredictX Telemetry Stream Ingestion Worker...")

    consumer = TelemetryConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        topic=settings.kafka_topic_telemetry,
        anomaly_topic=settings.kafka_topic_anomalies,
        batch_size=50,
        batch_timeout_sec=1.0,
    )

    def shutdown_handler(signum, frame):
        logger.info("Received termination signal. Gracefully shutting down worker...")
        consumer.running = False
        consumer.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info(
        f"Worker started. Subscribed to '{settings.kafka_topic_telemetry}' "
        f"on broker '{settings.kafka_bootstrap_servers}'."
    )
    consumer.consume_loop()


if __name__ == "__main__":
    main()
