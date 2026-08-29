from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PredictX"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://predictx:predictx@localhost:5432/predictx"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_telemetry: str = "sensor-telemetry-raw"
    kafka_topic_anomalies: str = "sensor-anomalies"
    kafka_consumer_group: str = "predictx-telemetry-group"

    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
