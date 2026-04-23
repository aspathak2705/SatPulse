from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import pandas as pd

from core.anomaly import adaptive_threshold
from data.loader import load_selected_parameters

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "raw"
RESULTS_PATH = BASE_DIR / "outputs" / "results.csv"
WINDOW_SIZE = 20
MAX_PLOT_POINTS = 5000
MAX_MARKER_POINTS = 1200
DEFAULT_VIEW_DAYS = 30

STATUS_TEXT = {
    "lstm_anomaly": "LSTM",
    "iso_anomaly": "Isolation Forest",
    "final_anomaly": "Final",
}

STATUS_COLORS = {
    "lstm_anomaly": "#fbbf24",
    "iso_anomaly": "#38bdf8",
    "final_anomaly": "#ef4444",
}


@lru_cache(maxsize=1)
def discover_parameters() -> list[str]:
    return sorted(
        path.name.replace("_stats_10min.parquet", "")
        for path in DATA_PATH.glob("*_stats_10min.parquet")
    )


@lru_cache(maxsize=1)
def read_results() -> pd.DataFrame:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Missing results file at {RESULTS_PATH}")

    results = pd.read_csv(RESULTS_PATH)
    for column in STATUS_TEXT:
        if column in results.columns:
            results[column] = (
                results[column]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({"true": True, "false": False})
                .fillna(results[column])
                .astype(bool)
            )

    results["threshold"] = adaptive_threshold(results["error"].to_numpy())
    return results


@lru_cache(maxsize=8)
def _load_dashboard_frame_cached(selected_params: tuple[str, ...]) -> pd.DataFrame:
    telemetry = load_selected_parameters(str(DATA_PATH), list(selected_params))
    if telemetry is None or telemetry.empty:
        raise ValueError("No telemetry data was loaded for the selected parameters.")

    telemetry = telemetry.ffill().dropna().copy()
    telemetry = telemetry.iloc[WINDOW_SIZE:].reset_index()
    timestamp_column = telemetry.columns[0]
    telemetry = telemetry.rename(columns={timestamp_column: "timestamp"})
    telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"])

    results = read_results()
    aligned_rows = min(len(telemetry), len(results))
    frame = telemetry.iloc[:aligned_rows].copy()
    results = results.iloc[:aligned_rows].copy()

    for column in ["time_index", "error", "threshold", *STATUS_TEXT]:
        frame[column] = results[column].values

    return frame


def load_dashboard_frame(selected_params: list[str]) -> pd.DataFrame:
    return _load_dashboard_frame_cached(tuple(selected_params)).copy()


def downsample_frame(frame: pd.DataFrame, preserve_columns: list[str] | None = None) -> pd.DataFrame:
    if len(frame) <= MAX_PLOT_POINTS:
        return frame

    step = math.ceil(len(frame) / MAX_PLOT_POINTS)
    sampled = frame.iloc[::step].copy()

    if preserve_columns:
        preserve_mask = frame[preserve_columns].any(axis=1)
        sampled = (
            pd.concat([sampled, frame.loc[preserve_mask]])
            .sort_values("timestamp")
            .drop_duplicates(subset="timestamp")
        )

    return sampled


def limit_points(frame: pd.DataFrame, max_points: int) -> pd.DataFrame:
    if len(frame) <= max_points:
        return frame

    step = math.ceil(len(frame) / max_points)
    return frame.iloc[::step].copy()


def metric_columns(frame: pd.DataFrame, selected_params: list[str]) -> list[str]:
    prefixes = tuple(f"{param}_" for param in selected_params)
    return [column for column in frame.columns if column.startswith(prefixes)]


def available_statistics(frame: pd.DataFrame, selected_params: list[str]) -> list[str]:
    stats = []
    for column in metric_columns(frame, selected_params):
        stats.append(column.split("_", 1)[1])
    return sorted(set(stats))


def normalize_series(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    normalized = frame.copy()
    for column in columns:
        series = normalized[column]
        spread = series.max() - series.min()
        normalized[column] = 0.0 if spread == 0 else (series - series.min()) / spread
    return normalized


def build_timeseries_figure(frame, selected_params, selected_stat, anomaly_flags, normalize, go):
    columns = [f"{param}_{selected_stat}" for param in selected_params if f"{param}_{selected_stat}" in frame]
    plot_frame = normalize_series(frame, columns) if normalize else frame
    chart_frame = downsample_frame(plot_frame, preserve_columns=anomaly_flags)

    figure = go.Figure()
    palette = ["#60a5fa", "#34d399", "#f97316", "#a78bfa", "#f472b6"]

    for index, column in enumerate(columns):
        figure.add_trace(
            go.Scattergl(
                x=chart_frame["timestamp"],
                y=chart_frame[column],
                mode="lines",
                name=column.replace(f"_{selected_stat}", ""),
                line={"width": 2, "color": palette[index % len(palette)]},
            )
        )

        for flag in anomaly_flags:
            flagged_rows = limit_points(
                chart_frame.loc[chart_frame[flag]],
                MAX_MARKER_POINTS,
            )
            if flagged_rows.empty:
                continue

            figure.add_trace(
                go.Scattergl(
                    x=flagged_rows["timestamp"],
                    y=flagged_rows[column],
                    mode="markers",
                    name=f"{column.replace(f'_{selected_stat}', '')} {STATUS_TEXT[flag]}",
                    marker={
                        "size": 8 if flag == "final_anomaly" else 6,
                        "color": STATUS_COLORS[flag],
                        "symbol": "circle" if flag == "final_anomaly" else "diamond",
                        "line": {"width": 1, "color": "#0f172a"},
                    },
                )
            )

    figure.update_layout(
        height=420,
        paper_bgcolor="#06111f",
        plot_bgcolor="#0b1b2b",
        font={"color": "#e2e8f0"},
        hovermode="x unified",
        margin={"l": 24, "r": 24, "t": 20, "b": 24},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.15)",
        title="Normalized value" if normalize else selected_stat,
    )
    return figure


def build_error_figure(frame, go):
    chart_frame = downsample_frame(frame, preserve_columns=["final_anomaly"])
    anomalous = limit_points(
        chart_frame.loc[chart_frame["final_anomaly"]],
        MAX_MARKER_POINTS,
    )

    figure = go.Figure()
    figure.add_trace(
        go.Scattergl(
            x=chart_frame["timestamp"],
            y=chart_frame["error"],
            mode="lines",
            name="Reconstruction Error",
            line={"color": "#38bdf8", "width": 2},
        )
    )
    figure.add_trace(
        go.Scattergl(
            x=chart_frame["timestamp"],
            y=chart_frame["threshold"],
            mode="lines",
            name="Adaptive Threshold",
            line={"color": "#fbbf24", "width": 2, "dash": "dash"},
        )
    )

    if not anomalous.empty:
        figure.add_trace(
            go.Scattergl(
                x=anomalous["timestamp"],
                y=anomalous["error"],
                mode="markers",
                name="Flagged Error",
                marker={"color": "#ef4444", "size": 8},
            )
        )

    figure.update_layout(
        height=360,
        paper_bgcolor="#06111f",
        plot_bgcolor="#0b1b2b",
        font={"color": "#e2e8f0"},
        hovermode="x unified",
        margin={"l": 24, "r": 24, "t": 20, "b": 24},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(148, 163, 184, 0.15)", title="Error")
    return figure


def inject_styles(st):
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stToolbar"] {
            right: 0.75rem;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.18), transparent 26%),
                radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.10), transparent 24%),
                linear-gradient(180deg, #06121f 0%, #08192a 52%, #07101d 100%);
            color: #f8fafc;
        }
        .stApp, .stApp p, .stApp label, .stMarkdown, .stText, .st-emotion-cache-10trblm,
        .st-emotion-cache-16txtl3, .st-emotion-cache-ue6h4q, .st-emotion-cache-1kyxreq {
            color: #f8fafc;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8, 15, 30, 0.98), rgba(7, 18, 31, 0.96));
            border-right: 1px solid rgba(148, 163, 184, 0.10);
        }
        section[data-testid="stSidebar"] * {
            color: #e5eefb !important;
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        .stDateInput > div > div,
        .stMultiSelect [data-baseweb="select"] > div {
            background: #0f2135 !important;
            border: 1px solid rgba(148, 163, 184, 0.28) !important;
        }
        .stButton > button {
            background: linear-gradient(180deg, #1d4ed8, #1e40af);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
        }
        .stButton > button:hover {
            background: linear-gradient(180deg, #2563eb, #1d4ed8);
            color: white;
        }
        .satpulse-hero {
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(96, 165, 250, 0.18);
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(13, 42, 68, 0.92), rgba(11, 24, 40, 0.96));
            margin-bottom: 1.25rem;
            box-shadow: 0 20px 50px rgba(2, 6, 23, 0.35);
        }
        .satpulse-title {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin: 0;
        }
        .satpulse-subtitle {
            margin: 0.35rem 0 0;
            color: #c7d7ea;
        }
        .satpulse-status {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            font-size: 0.95rem;
            font-weight: 600;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(10, 21, 35, 0.95), rgba(8, 16, 28, 0.92));
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
            padding: 0.75rem 0.9rem;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
        }
        div[data-testid="stMetricLabel"] {
            color: #b8c7db;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc;
        }
        .stSubheader {
            color: #f8fafc;
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 1.5rem;
            max-width: 1400px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    try:
        import plotly.graph_objects as go
        import streamlit as st
    except ImportError:
        print("Install dashboard dependencies first: pip install streamlit plotly")
        return

    st.set_page_config(
        page_title="SatPulse Dashboard",
        layout="wide",
    )
    inject_styles(st)

    available_params = discover_parameters()
    if not available_params:
        st.error(f"No parquet telemetry files were found in {DATA_PATH}.")
        return

    st.sidebar.title("Control Panel")
    selected_params = st.sidebar.multiselect(
        "Telemetry parameters",
        options=available_params,
        default=available_params[: min(2, len(available_params))],
    )

    if not selected_params:
        st.warning("Select at least one telemetry parameter to render the dashboard.")
        return

    try:
        dashboard_frame = load_dashboard_frame(selected_params)
    except Exception as exc:
        st.error(f"Unable to load dashboard data: {exc}")
        return

    stats = available_statistics(dashboard_frame, selected_params)
    if not stats:
        st.error("No telemetry statistics are available for the selected parameters.")
        return

    selected_stat = st.sidebar.selectbox(
        "Telemetry statistic",
        options=stats,
        index=stats.index("value_mean") if "value_mean" in stats else 0,
    )

    min_date = dashboard_frame["timestamp"].min().date()
    max_date = dashboard_frame["timestamp"].max().date()
    default_start = max(min_date, max_date - pd.Timedelta(days=DEFAULT_VIEW_DAYS))
    date_bounds = (min_date, max_date)
    chosen_range = st.sidebar.date_input(
        "Time range",
        value=(default_start, max_date),
        min_value=date_bounds[0],
        max_value=date_bounds[1],
    )

    if isinstance(chosen_range, tuple) and len(chosen_range) == 2:
        start_date, end_date = chosen_range
    else:
        start_date = end_date = chosen_range

    anomaly_flags = []
    for flag, label in STATUS_TEXT.items():
        default_enabled = flag == "final_anomaly"
        if st.sidebar.checkbox(label, value=default_enabled):
            anomaly_flags.append(flag)

    normalize = st.sidebar.toggle("Normalize series for comparison", value=False)
    if st.sidebar.button("Refresh data", use_container_width=True):
        st.rerun()

    filtered = dashboard_frame.loc[
        dashboard_frame["timestamp"].dt.date.between(start_date, end_date)
    ].copy()

    if filtered.empty:
        st.warning("No rows are available for the selected time range.")
        return

    active_anomaly_mask = (
        filtered[anomaly_flags].any(axis=1) if anomaly_flags else pd.Series(False, index=filtered.index)
    )
    status_flag = bool(active_anomaly_mask.any())
    status_text = "Anomaly Detected" if status_flag else "Normal"
    status_color = "#ef4444" if status_flag else "#22c55e"
    status_bg = "rgba(239, 68, 68, 0.14)" if status_flag else "rgba(34, 197, 94, 0.14)"

    st.markdown(
        f"""
        <div class="satpulse-hero">
            <p class="satpulse-title">SatPulse Dashboard</p>
            <p class="satpulse-subtitle">
                AI-assisted telemetry monitoring for anomaly detection across multi-sensor time series.
            </p>
            <span class="satpulse-status" style="color:{status_color}; background:{status_bg}; border:1px solid {status_color}33;">
                {status_text}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_points = len(filtered)
    total_anomalies = int(filtered["final_anomaly"].sum())
    anomaly_rate = (total_anomalies / total_points) * 100 if total_points else 0.0

    metrics = st.columns(3)
    metrics[0].metric("Total Data Points", f"{total_points:,}")
    metrics[1].metric("Total Anomalies", f"{total_anomalies:,}")
    metrics[2].metric("Anomaly Rate", f"{anomaly_rate:.2f}%")

    st.subheader("Telemetry Time Series")
    st.plotly_chart(
        build_timeseries_figure(
            filtered,
            selected_params,
            selected_stat,
            anomaly_flags,
            normalize,
            go,
        ),
        use_container_width=True,
    )

    detail_columns = st.columns([1.45, 1])

    with detail_columns[0]:
        st.subheader("Reconstruction Error")
        st.plotly_chart(build_error_figure(filtered, go), use_container_width=True)

    with detail_columns[1]:
        st.subheader("System Insights")
        st.markdown(
            f"""
            - Time span: `{filtered["timestamp"].min()}` to `{filtered["timestamp"].max()}`
            - LSTM flags: `{int(filtered["lstm_anomaly"].sum()):,}`
            - Isolation Forest flags: `{int(filtered["iso_anomaly"].sum()):,}`
            - Hybrid agreement: `{int((filtered["lstm_anomaly"] & filtered["iso_anomaly"]).sum()):,}`
            - Plot density cap: `{MAX_PLOT_POINTS:,}` points per chart
            """
        )

    st.subheader("Anomaly Table")
    table_columns = ["timestamp", "error", "threshold", *STATUS_TEXT]
    selected_metric_columns = [
        f"{param}_{selected_stat}"
        for param in selected_params
        if f"{param}_{selected_stat}" in filtered.columns
    ]
    anomaly_table = (
        filtered.loc[active_anomaly_mask, table_columns + selected_metric_columns]
        .sort_values("timestamp", ascending=False)
        .head(300)
    )
    st.dataframe(anomaly_table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
