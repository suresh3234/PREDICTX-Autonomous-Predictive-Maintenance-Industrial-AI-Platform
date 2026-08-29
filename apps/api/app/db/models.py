import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    machine_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    machine_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    machine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    vibration: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    rpm: Mapped[float] = mapped_column(Float, nullable=False)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current: Mapped[float] = mapped_column(Float, nullable=False)
    power: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    load: Mapped[float] = mapped_column(Float, nullable=False)
    operating_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    maintenance_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_maintenance: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    failure: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_type: Mapped[str] = mapped_column(String(100), nullable=False, default="None")
    rul: Mapped[float] = mapped_column(Float, nullable=False)
