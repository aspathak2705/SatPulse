from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.dashboard_data import build_dataset, clear_dataset_cache

app = FastAPI(
    title="SatPulse API",
    version="1.0.0",
    description="Backend API for the SatPulse telemetry anomaly dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/api/dashboard")
def get_dashboard_data(refresh: bool = False) -> dict:
    if refresh:
        clear_dataset_cache()
    return build_dataset()
