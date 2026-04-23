<div align="center">
  <img src="https://img.icons8.com/color/96/000000/satellite.png" alt="SatPulse Logo" width="80" />
  <h1 align="center">SatPulse</h1>
  <p align="center">
    <strong>An AI-assisted telemetry anomaly detection dashboard for satellite health monitoring</strong>
  </p>
  <p align="center">
    <a href="https://satpulse.onrender.com">Live Demo</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B" alt="Frontend" />
    <img src="https://img.shields.io/badge/Visualization-Plotly-3B82F6" alt="Visualization" />
    <img src="https://img.shields.io/badge/ML-LSTM%20Autoencoder%20%7C%20Isolation%20Forest-0F766E" alt="ML" />
    <img src="https://img.shields.io/badge/Data-Parquet%20%7C%20CSV-F59E0B" alt="Data" />
    <img src="https://img.shields.io/badge/Deployment-Render-46E3B7" alt="Deployment" />
  </p>
</div>

---

## Overview

**SatPulse** is a telemetry monitoring and anomaly detection project designed to help engineers inspect unusual behavior across satellite sensor streams.

The current system combines:

- a **Streamlit dashboard** for interactive monitoring
- **Plotly visualizations** for time-series and anomaly inspection
- a **hybrid anomaly detection pipeline** using an LSTM autoencoder and Isolation Forest
- **Parquet-based telemetry inputs** and generated anomaly outputs stored as `results.csv`

The product experience is centered on fast anomaly review: selecting telemetry parameters, filtering by time, comparing sensor behavior, and inspecting detected outliers in a single dashboard.

<br>

## Live Deployment

The dashboard is deployed on Render:

- **Live App:** [https://satpulse.onrender.com](https://satpulse.onrender.com)

<br>

## Key Features

- **Telemetry Monitoring Dashboard:** Visualizes multi-sensor time-series data with an interactive, dark-themed dashboard.
- **Hybrid Anomaly Detection:** Combines sequence reconstruction error from an LSTM autoencoder with Isolation Forest outlier detection.
- **Anomaly Overlay Visualization:** Highlights detected anomalies directly on the telemetry plots for faster inspection.
- **Reconstruction Error Analysis:** Displays error trends with an adaptive threshold to support debugging and interpretation.
- **Responsive Investigation Workflow:** Includes KPI cards, parameter filters, anomaly toggles, and anomaly tables for engineering review.
- **File-Based Deployment Simplicity:** Runs directly from parquet and CSV artifacts without requiring a database for lightweight deployments.

<br>

## Architecture & Tech Stack

SatPulse is currently organized as a lightweight ML + dashboard pipeline.

### Dashboard Layer

- **Framework:** Streamlit
- **Visualization:** Plotly
- **Styling:** Custom Streamlit theming and CSS
- **Deployment Target:** Render

### Detection Layer

- **Sequence Model:** LSTM Autoencoder
- **Outlier Model:** Isolation Forest
- **Thresholding:** Adaptive rolling threshold over reconstruction error
- **Pipeline Script:** `pipeline/detect.py`

### Data Layer

- **Telemetry Source:** Parquet files in `data/raw/`
- **Detection Output:** `outputs/results.csv`
- **Model Artifact:** `models/lstm_autoencoder.pth`
- **Processing Tools:** Pandas, NumPy

<br>

## How It Works

At a high level, the system follows this flow:

1. telemetry statistics are loaded from parquet files
2. the data is cleaned and transformed into rolling sequences
3. the LSTM autoencoder reconstructs the sequences
4. reconstruction error is computed for each sequence
5. an adaptive threshold flags likely sequence anomalies
6. Isolation Forest detects point-wise outliers on the flattened feature space
7. both signals are merged into a final anomaly label
8. the dashboard reads the generated anomaly output and overlays it on telemetry trends

<br>

## Dashboard Modules

The current dashboard experience includes:

- **Header Status:** Project title and overall anomaly status
- **Control Panel:** Parameter selection, statistic selection, time-range filter, and anomaly-layer toggles
- **KPI Summary:** Total data points, total anomalies, and anomaly rate
- **Telemetry Time Series:** Interactive multi-line chart with anomaly markers
- **Reconstruction Error View:** Error curve plus adaptive threshold line
- **System Insights:** Quick operational counts for anomaly categories
- **Anomaly Table:** Filtered anomaly records for debugging and validation

<br>

## Project Structure

```text
SatPulse/
├── core/                  # Preprocessing and anomaly helper utilities
├── dashboard/             # Streamlit dashboard
├── data/
│   └── raw/               # Source telemetry parquet files
├── explainability/        # Explainability utilities
├── models/                # Trained model artifacts and model definitions
├── outputs/               # Generated detection results
├── pipeline/              # Training and detection scripts
├── simulation/            # Streaming / simulation utilities
├── .streamlit/            # Streamlit deployment config
├── render.yaml            # Render deployment config
├── requirements.txt
└── README.md
```

<br>

## Getting Started

### Prerequisites

- Python `3.11+`
- `pip`
- A virtual environment is recommended

### 1. Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

On Windows with the local virtual environment:

```powershell
.\venv\Scripts\python -m pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run dashboard/app.py
```

On Windows PowerShell:

```powershell
.\venv\Scripts\python -m streamlit run dashboard\app.py
```

### 3. Generate Detection Results

If `outputs/results.csv` needs to be regenerated:

```bash
python pipeline/detect.py
```

This script loads telemetry data, runs the hybrid anomaly detection pipeline, and writes fresh results to `outputs/results.csv`.

<br>

## Data Inputs

The dashboard currently depends on local project files instead of a database.

### Telemetry Files

- `data/raw/AMT00102_stats_10min.parquet`
- `data/raw/AMT00103_stats_10min.parquet`

These files contain 10-minute telemetry statistics such as:

- `value_min`
- `value_q05`
- `value_q95`
- `value_max`
- `value_mean`
- `value_median`
- `value_std`
- `value_skew`
- `value_sum`
- `value_last`
- `value_count`

### Generated Results

`outputs/results.csv` includes:

- `time_index`
- `error`
- `lstm_anomaly`
- `iso_anomaly`
- `final_anomaly`

<br>

## Deployment

### Render

The project is configured for Render deployment using:

- [render.yaml](C:\Users\athar\OneDrive\Documents\projects\SatPulse\render.yaml)
- [config.toml](C:\Users\athar\OneDrive\Documents\projects\SatPulse\.streamlit\config.toml)

Current production deployment:

- [https://satpulse.onrender.com](https://satpulse.onrender.com)

### Render Setup Notes

- **Service Type:** Web Service
- **Runtime:** Python
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`

For the current version, deployment works because the app reads telemetry and output files directly from the repository.

<br>

## Current Limitations

- The dashboard currently reads from local parquet and CSV artifacts, which is fine for lightweight deployments but not ideal for larger real-time systems.
- The deployed app is optimized for visualization and inspection, not for online model retraining.
- The current pipeline is based on precomputed telemetry files and does not yet include a live streaming ingestion layer.
- Explainability and root-cause analysis modules are present in the repo, but the dashboard currently focuses on monitoring rather than advanced explanation workflows.

<br>

## Future Improvements

- add real-time telemetry ingestion and streaming updates
- move from file-based artifacts to a more scalable storage layer for larger deployments
- add richer explainability views for anomaly attribution
- support more telemetry parameters and more flexible mission-level filtering
- improve operational readiness with automated tests, health checks, and monitoring

---

<div align="center">
  <p>Built for telemetry intelligence, anomaly detection, and mission monitoring.</p>
</div>
