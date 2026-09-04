import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

# Resolve apps/api path so we can import db sessions and models
API_PATH = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.db.models import Machine, TelemetryLog
from app.db.session import SessionLocal


def seed_db():
    db: Session = SessionLocal()
    try:
        # 1. Load CSV data
        sensor_csv = "data/synthetic/sensor_readings.csv"
        if not os.path.exists(sensor_csv):
            print(f"Error: Sensor readings file not found at {sensor_csv}")
            return

        df = pd.read_csv(sensor_csv)

        # 2. Extract unique machines and seed them
        machine_codes = df["machine_id"].unique()
        print(f"Found {len(machine_codes)} unique machines to seed.")

        machine_map = {}
        for code in machine_codes:
            # Check if machine already exists in the database
            existing = db.scalar(select(Machine).where(Machine.machine_code == code))
            if existing:
                machine_map[code] = existing.id
                print(f"Machine {code} already exists in database.")
            else:
                m_type = "Medium Duty"
                if "machine_type" in df.columns:
                    m_type = df[df["machine_id"] == code]["machine_type"].iloc[0]

                mach = Machine(machine_code=code, machine_type=m_type)
                db.add(mach)
                db.flush()  # Generate UUID id immediately
                machine_map[code] = mach.id
                print(f"Created machine entity: {code} ({m_type})")

        # 3. Seed telemetry logs (limit to last 200 readings per machine for performance)
        print("Seeding telemetry logs...")
        logs_to_add = []
        for code in machine_codes:
            df_mach = df[df["machine_id"] == code].sort_values(by="timestamp").tail(200)
            for _, row in df_mach.iterrows():
                last_maint = None
                if "last_maintenance" in row and pd.notna(row["last_maintenance"]):
                    last_maint = pd.to_datetime(row["last_maintenance"])

                log = TelemetryLog(
                    machine_id=machine_map[code],
                    timestamp=pd.to_datetime(row["timestamp"]),
                    temperature=float(row["temperature"]),
                    vibration=float(row["vibration"]),
                    pressure=float(row["pressure"]),
                    rpm=float(row["rpm"]),
                    voltage=float(row["voltage"]),
                    current=float(row["current"]),
                    power=float(row["power"]),
                    humidity=float(row["humidity"]),
                    load=float(row["load"]),
                    operating_hours=float(row["operating_hours"]),
                    maintenance_count=int(row["maintenance_count"]),
                    last_maintenance=last_maint,
                    failure=int(row["failure"]),
                    failure_type=str(row["failure_type"]),
                    rul=float(row["RUL"])
                )
                logs_to_add.append(log)

        db.add_all(logs_to_add)
        db.commit()
        print(f"Successfully seeded {len(logs_to_add)} telemetry records!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
