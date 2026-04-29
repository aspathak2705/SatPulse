from __future__ import annotations

import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.dashboard_data import build_dataset, clear_dataset_cache

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5180",
    "http://127.0.0.1:5180",
    "https://satpulse.vercel.app",
]


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("ALLOWED_ORIGINS", "")
    extra_origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
    return [*DEFAULT_ALLOWED_ORIGINS, *extra_origins]

app = FastAPI(
    title="SatPulse API",
    version="1.0.0",
    description="Backend API for the SatPulse telemetry anomaly dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
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
