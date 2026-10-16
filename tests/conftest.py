import os
import sys
from pathlib import Path

# Programmatically configure test database environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Programmatically add repository root and apps/api to sys.path
ROOT_PATH = Path(__file__).resolve().parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

API_PATH = ROOT_PATH / "apps" / "api"
if str(API_PATH) not in sys.path:
    sys.path.insert(0, str(API_PATH))

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_synthetic_sensor_data():
    sensor_path = ROOT_PATH / "data" / "synthetic" / "sensor_readings.csv"
    if not sensor_path.exists():
        sensor_path.parent.mkdir(parents=True, exist_ok=True)
        import subprocess

        subprocess.run(
            [
                sys.executable,
                str(ROOT_PATH / "scripts" / "generate_sensor_data.py"),
                "--machines",
                "5",
                "--days",
                "5",
            ],
            check=True,
        )

