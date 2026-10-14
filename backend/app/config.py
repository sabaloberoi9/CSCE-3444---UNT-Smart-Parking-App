"""App settings, read from environment variables (TR-52, TR-54, TR-68)."""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings:
    def __init__(self) -> None:
        self.env = os.getenv("APP_ENV", "development")
        # Demo mode: simulated data and the "Simulated data" label in the app (TR-69)
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        # Data source switch (TR-68): "simulated" now; a real UNT feed can be added later
        self.data_source = os.getenv("DATA_SOURCE", "simulated")
        self.data_dir = Path(os.getenv("DATA_DIR", BACKEND_DIR / "data"))
        self.db_path = Path(os.getenv("DB_PATH", self.data_dir / "app.db"))
        # Never use this default outside a class demo - set JWT_SECRET in production
        self.jwt_secret = os.getenv("JWT_SECRET", "dev-only-change-me-unt-parking-demo-secret")
        self.jwt_hours = int(os.getenv("JWT_HOURS", "12"))
        # TODO (next milestone): MODEL_PATH, ROUTING_PROVIDER / OSRM_URL, TICK_SECONDS, DEMO_START
        # once prediction, routing and the live feed are built.


settings = Settings()
