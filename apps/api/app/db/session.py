import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

db_url = os.getenv("DATABASE_URL", settings.database_url)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=not db_url.startswith("sqlite"),
        connect_args=connect_args,
    )
except Exception:
    # Graceful fallback to local SQLite database if Postgres driver is unavailable
    engine = create_engine(
        "sqlite:///./predictx.db",
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
