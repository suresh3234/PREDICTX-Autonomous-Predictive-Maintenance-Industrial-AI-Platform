import numpy as np
import pandas as pd


class FeaturePipeline:
    def __init__(self, rolling_windows=None):
        if rolling_windows is None:
            # 6 steps = 1 hour (10-min interval), 24 steps = 4 hours
            self.rolling_windows = [6, 24]
        else:
            self.rolling_windows = rolling_windows

    def fit(self, df: pd.DataFrame):
        """Pass-through for interface compatibility."""
        return self

    def transform(self, df: pd.DataFrame, drop_na: bool = True) -> pd.DataFrame:
        """
        Transforms raw validated sensor DataFrame by appending rolling, lag, rate-of-change,
        interaction, temporal, and machine-level features.

        All engineered features are prefixed with 'feature_' to clearly demarcate
        them from targets and raw sensor data, preventing target leakage.
        """
        if df.empty:
            return pd.DataFrame()

        df_out = df.copy()

        # Sort values to guarantee correct temporal sequences
        df_out["timestamp"] = pd.to_datetime(df_out["timestamp"])
        df_out = df_out.sort_values(by=["machine_id", "timestamp"]).reset_index(
            drop=True
        )

        # 1. Temporal features
        df_out["feature_hour"] = df_out["timestamp"].dt.hour
        df_out["feature_day"] = df_out["timestamp"].dt.day
        df_out["feature_week"] = df_out["timestamp"].dt.isocalendar().week.astype(int)
        df_out["feature_month"] = df_out["timestamp"].dt.month
        df_out["feature_operating_cycle"] = (df_out["operating_hours"] // 100).astype(
            int
        )

        # 2. Machine-level features
        last_maint = pd.to_datetime(df_out["last_maintenance"])
        df_out["feature_days_since_maintenance"] = (
            df_out["timestamp"] - last_maint
        ).dt.total_seconds() / (24 * 3600)
        df_out["feature_machine_age_hours"] = df_out["operating_hours"]

        # 3. Interaction features
        df_out["feature_temp_x_vib"] = df_out["temperature"] * df_out["vibration"]
        df_out["feature_curr_x_rpm"] = df_out["current"] * df_out["rpm"]
        df_out["feature_press_x_load"] = df_out["pressure"] * df_out["load"]

        # 4. Grouped operations: Lag and Rolling features
        sensor_cols = ["temperature", "vibration", "pressure", "current", "power"]
        lags = [1, 5, 10, 20]

        for col in sensor_cols:
            # Lags
            for lag in lags:
                df_out[f"feature_{col}_lag_{lag}"] = df_out.groupby("machine_id")[
                    col
                ].shift(lag)

            # Rate of change
            lag_col = f"feature_{col}_lag_1"
            # delta (first difference)
            df_out[f"feature_{col}_delta"] = df_out[col] - df_out[lag_col]
            # percentage change (with epsilon to prevent division by zero)
            df_out[f"feature_{col}_pct_change"] = (
                df_out[f"feature_{col}_delta"] / (df_out[lag_col] + 1e-8)
            ) * 100.0

            # Acceleration (second difference)
            lag_col_2 = df_out.groupby("machine_id")[col].shift(2)
            df_out[f"feature_{col}_acceleration"] = (
                df_out[col] - 2 * df_out[lag_col] + lag_col_2
            )

        # 5. Rolling features
        for window in self.rolling_windows:
            for col in sensor_cols:
                grouped = df_out.groupby("machine_id")[col]
                # Rolling stats (trailing windows)
                df_out[f"feature_{col}_roll_mean_{window}"] = (
                    grouped.rolling(window, min_periods=1)
                    .mean()
                    .reset_index(level=0, drop=True)
                )
                df_out[f"feature_{col}_roll_std_{window}"] = (
                    grouped.rolling(window, min_periods=1)
                    .std()
                    .reset_index(level=0, drop=True)
                    .fillna(0.0)
                )
                df_out[f"feature_{col}_roll_min_{window}"] = (
                    grouped.rolling(window, min_periods=1)
                    .min()
                    .reset_index(level=0, drop=True)
                )
                df_out[f"feature_{col}_roll_max_{window}"] = (
                    grouped.rolling(window, min_periods=1)
                    .max()
                    .reset_index(level=0, drop=True)
                )

        # 6. Vibration Domain Specific Features (trailing window)
        grouped_vib = df_out.groupby("machine_id")["vibration"]
        for window in self.rolling_windows:
            # Vibration variance
            df_out[f"feature_vibration_var_{window}"] = (
                grouped_vib.rolling(window, min_periods=1)
                .var()
                .reset_index(level=0, drop=True)
                .fillna(0.0)
            )

            # Vibration RMS
            vib_sq = df_out["vibration"] ** 2
            df_out[f"feature_vibration_rms_{window}"] = np.sqrt(
                vib_sq.groupby(df_out["machine_id"])
                .rolling(window, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )

            # Vibration Peak (absolute peak value)
            vib_abs = df_out["vibration"].abs()
            df_out[f"feature_vibration_peak_{window}"] = (
                vib_abs.groupby(df_out["machine_id"])
                .rolling(window, min_periods=1)
                .max()
                .reset_index(level=0, drop=True)
            )

            # Vibration Crest Factor = Peak / RMS
            df_out[f"feature_vibration_crest_factor_{window}"] = df_out[
                f"feature_vibration_peak_{window}"
            ] / (df_out[f"feature_vibration_rms_{window}"] + 1e-8)

        if drop_na:
            # Drop rows with NaNs generated by shifting/lags in feature columns
            feature_cols = [col for col in df_out.columns if col.startswith("feature_")]
            df_out = df_out.dropna(subset=feature_cols).reset_index(drop=True)

        return df_out
