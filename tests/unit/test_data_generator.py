import os
import tempfile

import pandas as pd

from scripts.generate_sensor_data import generate_sensor_data


class ArgsPlaceholder:
    def __init__(
        self,
        machines=2,
        days=2,
        freq=30,
        failure_rate=0.5,
        anomaly_rate=0.01,
        noise_level=1.0,
        output_dir=None,
        seed=42,
    ):
        self.machines = machines
        self.days = days
        self.freq = freq
        self.failure_rate = failure_rate
        self.anomaly_rate = anomaly_rate
        self.noise_level = noise_level
        self.output_dir = output_dir
        self.seed = seed


def test_sensor_data_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = ArgsPlaceholder(machines=2, days=3, freq=20, output_dir=tmpdir)
        generate_sensor_data(args)

        # Assert files were created
        readings_path = os.path.join(tmpdir, "sensor_readings.csv")
        machines_path = os.path.join(tmpdir, "machines.csv")
        assert os.path.exists(readings_path)
        assert os.path.exists(machines_path)

        # Validate machine metadata
        df_machines = pd.read_csv(machines_path)
        assert len(df_machines) == 2
        assert list(df_machines.columns) == [
            "machine_id",
            "machine_type",
            "temp",
            "vib",
            "press",
            "rpm",
            "volt",
            "curr",
            "hum",
            "load",
        ]

        # Validate sensor readings
        df_readings = pd.read_csv(readings_path)
        expected_steps = int((3 * 24 * 60) / 20) * 2  # 216 steps * 2 machines = 432
        assert len(df_readings) == expected_steps

        # Validate column schema
        expected_cols = [
            "machine_id",
            "timestamp",
            "machine_type",
            "temperature",
            "vibration",
            "pressure",
            "rpm",
            "voltage",
            "current",
            "power",
            "humidity",
            "load",
            "operating_hours",
            "maintenance_count",
            "last_maintenance",
            "failure",
            "failure_type",
            "RUL",
        ]
        assert list(df_readings.columns) == expected_cols

        # Ensure operating hours increase monotonically per machine
        m1_readings = df_readings[df_readings["machine_id"] == "M1000"]
        assert (m1_readings["operating_hours"].diff().dropna() >= 0).all()

        # Ensure RUL counts down correctly when failure is scheduled
        failures = df_readings[df_readings["failure"] == 1]
        for idx, row in failures.iterrows():
            m_id = row["machine_id"]
            # Look at prior step
            prev_row = df_readings[
                (df_readings["machine_id"] == m_id) & (df_readings.index < idx)
            ].iloc[-1]
            # Prior step should have a non-zero, small RUL counting down to 0
            assert prev_row["RUL"] > 0
            assert prev_row["RUL"] <= 5 * 24  # within degradation window (5 days)
