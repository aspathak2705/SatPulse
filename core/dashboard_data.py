from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from core.anomaly import adaptive_threshold
from data.loader import load_selected_parameters

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "raw"
RESULTS_PATH = BASE_DIR / "outputs" / "results.csv"
WINDOW_SIZE = 20
EXPORT_DAYS = 30


def discover_parameters() -> list[str]:
    return sorted(
        path.name.replace("_stats_10min.parquet", "")
        for path in DATA_PATH.glob("*_stats_10min.parquet")
    )


def read_results() -> pd.DataFrame:
    results = pd.read_csv(RESULTS_PATH)
    for column in ["lstm_anomaly", "iso_anomaly", "final_anomaly"]:
        results[column] = results[column].astype(bool)
    results["threshold"] = adaptive_threshold(results["error"].to_numpy())
    return results


@lru_cache(maxsize=1)
def build_dataset() -> dict:
    selected_params = discover_parameters()
    telemetry = load_selected_parameters(str(DATA_PATH), selected_params)
    if telemetry is None or telemetry.empty:
      raise ValueError("No telemetry data found for dashboard dataset.")

    telemetry = telemetry.ffill().dropna().copy()
    telemetry = telemetry.iloc[WINDOW_SIZE:].reset_index()
    telemetry = telemetry.rename(columns={telemetry.columns[0]: "timestamp"})
    telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"])

    results = read_results()
    aligned_rows = min(len(telemetry), len(results))
    frame = telemetry.iloc[:aligned_rows].copy()
    results = results.iloc[:aligned_rows].copy()

    frame["error"] = results["error"].values
    frame["threshold"] = results["threshold"].values
    frame["lstmAnomaly"] = results["lstm_anomaly"].values
    frame["isoAnomaly"] = results["iso_anomaly"].values
    frame["finalAnomaly"] = results["final_anomaly"].values

    latest_timestamp = frame["timestamp"].max()
    window_start = latest_timestamp - pd.Timedelta(days=EXPORT_DAYS)
    frame = frame.loc[frame["timestamp"] >= window_start].copy()

    parameter_prefixes = tuple(f"{parameter}_" for parameter in selected_params)
    statistics = sorted(
        {
            column.split("_", 1)[1]
            for column in frame.columns
            if column.startswith(parameter_prefixes)
        }
    )

    records = []
    for row in frame.itertuples(index=False):
        item = {"timestamp": row.timestamp.isoformat()}
        for column, value in row._asdict().items():
            if column == "timestamp":
                continue
            if isinstance(value, bool):
                item[column] = value
            elif pd.isna(value):
                item[column] = None
            else:
                item[column] = round(float(value), 6)
        records.append(item)

    total_points = len(frame)
    final_alerts = int(frame["finalAnomaly"].sum())
    anomaly_rate = round((final_alerts / total_points) * 100, 2) if total_points else 0.0

    return {
        "generatedAt": pd.Timestamp.now("UTC").isoformat(),
        "windowDays": EXPORT_DAYS,
        "defaultRangeDays": 7,
        "defaultStatistic": "value_mean",
        "parameters": selected_params,
        "statistics": statistics,
        "summary": {
            "totalPoints": total_points,
            "finalAlerts": final_alerts,
            "anomalyRate": anomaly_rate,
            "lstmAlerts": int(frame["lstmAnomaly"].sum()),
            "isoAlerts": int(frame["isoAnomaly"].sum()),
        },
        "records": records,
    }


def clear_dataset_cache() -> None:
    build_dataset.cache_clear()
