from __future__ import annotations

import json
from pathlib import Path

from core.dashboard_data import build_dataset

BASE_DIR = Path(__file__).resolve().parents[1]
EXPORT_PATH = BASE_DIR / "frontend" / "public" / "dashboard-data.json"


def main() -> None:
    dataset = build_dataset()
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EXPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(dataset, handle, indent=2)
    print(f"Exported {len(dataset['records'])} records to {EXPORT_PATH}")


if __name__ == "__main__":
    main()
