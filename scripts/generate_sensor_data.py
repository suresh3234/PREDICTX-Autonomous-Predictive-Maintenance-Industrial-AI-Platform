import argparse
import datetime
import os
import random

import numpy as np
import pandas as pd

# Constants for baseline configuration of different machine types
MACHINE_TYPES = ["Industrial Motor", "CNC Mill", "Hydraulic Pump"]

BASELINES = {
    "Industrial Motor": {
        "temp": 65.0,  # C
        "vib": 1.8,  # mm/s
        "press": 35.0,  # PSI
        "rpm": 1800.0,
        "volt": 220.0,  # V
        "curr": 15.0,  # A
        "hum": 45.0,  # %
        "load": 70.0,  # %
    },
    "CNC Mill": {
        "temp": 50.0,
        "vib": 2.5,
        "press": 80.0,
        "rpm": 3200.0,
        "volt": 415.0,
        "curr": 25.0,
        "hum": 40.0,
        "load": 65.0,
    },
    "Hydraulic Pump": {
        "temp": 55.0,
        "vib": 1.2,
        "press": 120.0,
        "rpm": 1200.0,
        "volt": 220.0,
        "curr": 12.0,
        "hum": 50.0,
        "load": 80.0,
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="PredictX Synthetic Industrial Sensor Data Generator"
    )
    parser.add_argument(
        "--machines", type=int, default=10, help="Number of machines to simulate"
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Number of simulation days"
    )
    parser.add_argument(
        "--freq", type=int, default=10, help="Sampling frequency in minutes"
    )
    parser.add_argument(
        "--failure-rate",
        type=float,
        default=0.15,
        help="Probability of scheduling a failure cycle per machine",
    )
    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.005,
        help="Rate of random, transient anomalies (spikes)",
    )
    parser.add_argument(
        "--noise-level",
        type=float,
        default=1.0,
        help="Standard deviation scaling factor for sensor noise",
    )
    parser.add_argument(
        "--output-dir", type=str, default="data/synthetic", help="Output directory path"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    return parser.parse_args()


def generate_sensor_data(args):
    # Set random seed
    random.seed(args.seed)
    np.random.seed(args.seed)

    # Calculate steps
    start_time = datetime.datetime.now() - datetime.timedelta(days=args.days)
    time_delta = datetime.timedelta(minutes=args.freq)
    total_steps = int((args.days * 24 * 60) / args.freq)

    os.makedirs(args.output_dir, exist_ok=True)
    all_readings = []

    print(
        f"Starting data generation for {args.machines} machines over {args.days} days ({total_steps} steps per machine)..."
    )

    # Generate metadata for machines
    machine_metadata = []
    for i in range(args.machines):
        m_id = f"M{1000 + i}"
        m_type = random.choice(MACHINE_TYPES)
        machine_metadata.append(
            {"machine_id": m_id, "machine_type": m_type, "baselines": BASELINES[m_type]}
        )

    # Simulate each machine
    for machine in machine_metadata:
        m_id = machine["machine_id"]
        m_type = machine["machine_type"]
        baselines = machine["baselines"]

        print(f"Simulating machine {m_id} ({m_type})...")

        # Initialize trackers
        op_hours = 0.0
        maint_count = 0
        last_maint_time = start_time

        # Determine failure schedule
        # To avoid uniform distribution, we create failure cycles.
        steps_until_next_failure = -1
        current_failure_type = None

        if random.random() < args.failure_rate:
            # Schedule a failure somewhere in the middle-to-end of the steps
            steps_until_next_failure = random.randint(
                int(total_steps * 0.3), total_steps - 10
            )
            current_failure_type = random.choice(
                [
                    "Bearing Failure",
                    "Overheating",
                    "Electrical Failure",
                    "Pressure Leak",
                    "Cooling System Failure",
                ]
            )

        for step in range(total_steps):
            current_time = start_time + step * time_delta
            op_hours += args.freq / 60.0

            # 1. Base healthy values with temporal cycles (daily temperature oscillations)
            hour_of_day = current_time.hour
            daily_cycle = np.sin(2 * np.pi * hour_of_day / 24.0)

            temp = baselines["temp"] + daily_cycle * 2.0
            vib = baselines["vib"] + (
                np.sin(2 * np.pi * step / 100.0) * 0.1
            )  # slow vibration wave
            press = baselines["press"]
            rpm = baselines["rpm"]
            volt = baselines["volt"]
            curr = baselines["curr"]
            hum = baselines["hum"] + daily_cycle * -5.0
            load = baselines["load"] + (np.cos(2 * np.pi * step / 50.0) * 5.0)

            # 2. Add realistic AutoRegressive AR(1) drift + Gaussian noise
            temp += np.random.normal(0, 0.5 * args.noise_level)
            vib += np.random.normal(0, 0.1 * args.noise_level)
            press += np.random.normal(0, 1.0 * args.noise_level)
            rpm += np.random.normal(0, 10.0 * args.noise_level)
            volt += np.random.normal(0, 1.5 * args.noise_level)
            curr += np.random.normal(0, 0.3 * args.noise_level)
            hum += np.random.normal(0, 1.0 * args.noise_level)

            # Power consumption is highly correlated with voltage and current: P = V * I * pf
            power = (volt * curr * 0.85) / 1000.0  # kW

            # 3. Simulate degradation path if approaching a scheduled failure
            is_failure_step = False
            failure_event_occurred = 0
            fail_type_logged = "None"
            rul_hours = 9999.0  # default when healthy / no failure scheduled

            if steps_until_next_failure >= 0:
                steps_remaining = steps_until_next_failure - step
                rul_hours = (steps_remaining * args.freq) / 60.0

                # If we are within 5 days (720 steps at 10-min interval) of failure, start degradation
                degrad_window = int((5 * 24 * 60) / args.freq)
                if steps_remaining <= degrad_window and steps_remaining >= 0:
                    # Normalized degradation index: 0 (start) to 1 (failure)
                    factor = 1.0 - (steps_remaining / float(degrad_window))

                    if current_failure_type == "Bearing Failure":
                        # Temperature & vibration increase, current variance increases
                        vib += (factor**2) * 5.0  # exponential increase in vibration
                        temp += factor * 18.0
                        curr += np.random.normal(0, factor * 2.0)
                    elif current_failure_type == "Overheating":
                        # Sudden linear increase in temperature, slight vibration rise
                        temp += factor * 28.0
                        vib += factor * 0.8
                    elif current_failure_type == "Electrical Failure":
                        # Voltage fluctuates wildly, power drops or current spikes
                        volt += np.sin(steps_remaining) * factor * 25.0
                        curr += factor * 10.0
                    elif current_failure_type == "Pressure Leak":
                        # Slow drop in pressure, temperature climbs due to hydraulic load
                        press -= factor * (baselines["press"] * 0.5)
                        temp += factor * 8.0
                    elif current_failure_type == "Cooling System Failure":
                        # Massive rapid rise in temperature, loss of pressure
                        temp += factor * 35.0
                        press -= factor * (baselines["press"] * 0.3)

                # Check if this is the failure step
                if steps_remaining == 0:
                    is_failure_step = True
                    failure_event_occurred = 1
                    fail_type_logged = current_failure_type
                    rul_hours = 0.0

            # 4. Inject transient anomalies (spikes/dropouts)
            if not is_failure_step and random.random() < args.anomaly_rate:
                anomaly_type = random.choice(["spike", "dropout"])
                sensor_to_affect = random.choice(["temp", "vib", "press", "volt"])

                if anomaly_type == "spike":
                    if sensor_to_affect == "temp":
                        temp += 20.0
                    elif sensor_to_affect == "vib":
                        vib += 6.0
                    elif sensor_to_affect == "press":
                        press += 45.0
                    elif sensor_to_affect == "volt":
                        volt += 40.0
                else:  # dropout
                    if sensor_to_affect == "temp":
                        temp = 10.0
                    elif sensor_to_affect == "vib":
                        vib = 0.05
                    elif sensor_to_affect == "press":
                        press = 5.0
                    elif sensor_to_affect == "volt":
                        volt = 10.0

            # Append reading
            all_readings.append(
                {
                    "machine_id": m_id,
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "machine_type": m_type,
                    "temperature": round(temp, 2),
                    "vibration": round(vib, 3),
                    "pressure": round(press, 2),
                    "rpm": round(rpm, 1),
                    "voltage": round(volt, 1),
                    "current": round(curr, 2),
                    "power": round(power, 3),
                    "humidity": round(hum, 2),
                    "load": round(load, 1),
                    "operating_hours": round(op_hours, 2),
                    "maintenance_count": maint_count,
                    "last_maintenance": last_maint_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "failure": failure_event_occurred,
                    "failure_type": fail_type_logged,
                    "RUL": round(rul_hours, 1),
                }
            )

            # 5. Handle post-failure repair (Maintenance event)
            if is_failure_step:
                # Reset system
                maint_count += 1
                last_maint_time = current_time
                # Reschedule or end failure cycle
                if random.random() < args.failure_rate:
                    # schedule another failure further out
                    remaining_steps = total_steps - step
                    if remaining_steps > 150:
                        steps_until_next_failure = step + random.randint(
                            100, remaining_steps - 10
                        )
                        current_failure_type = random.choice(
                            [
                                "Bearing Failure",
                                "Overheating",
                                "Electrical Failure",
                                "Pressure Leak",
                                "Cooling System Failure",
                            ]
                        )
                    else:
                        steps_until_next_failure = -1
                else:
                    steps_until_next_failure = -1

    # Convert to DataFrames and Save
    df_readings = pd.DataFrame(all_readings)
    df_readings.to_csv(
        os.path.join(args.output_dir, "sensor_readings.csv"), index=False
    )

    df_machines = pd.DataFrame(machine_metadata)
    # Explode baselines into flat columns for the machines.csv file
    df_machines_flat = pd.concat(
        [
            df_machines.drop(columns=["baselines"]),
            df_machines["baselines"].apply(pd.Series),
        ],
        axis=1,
    )
    df_machines_flat.to_csv(os.path.join(args.output_dir, "machines.csv"), index=False)

    print(f"Data generation complete! Saved files to {args.output_dir}")
    print(f"Generated {len(df_readings)} rows of sensor data.")


if __name__ == "__main__":
    args = parse_args()
    generate_sensor_data(args)
