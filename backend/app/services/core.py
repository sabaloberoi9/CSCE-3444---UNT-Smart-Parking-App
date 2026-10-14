"""ParkingService: the application logic behind every API endpoint.

Kept free of web-framework code so it can be tested directly (see tests/).

60% milestone: users (authentication + profile) and read-only campus data are done.
Sections marked TODO are the remaining features for the next milestone.
"""

from __future__ import annotations

import json
import re
import secrets
from datetime import datetime
from typing import Any

from app.campus import BUILDINGS, LOTS, PERMIT_TYPES, POI_CATEGORIES, POIS
from app.config import Settings
from app.services.db import Database
from app.services.security import create_token, hash_password, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
HM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
MIN_PASSWORD = 8


class ServiceError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


class ParkingService:
    def __init__(self, settings: Settings, reset: bool = False) -> None:
        self.settings = settings
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = Database(settings.db_path)
        if reset:
            self.db.reset_and_seed(settings.data_dir)
        else:
            self.db.seed(settings.data_dir)

    # ======================================================================
    # Authentication (FR-1, TR-2, TR-3)
    # ======================================================================
    def _session(self, row: dict[str, Any]) -> dict[str, Any]:
        token = create_token(row["id"], row["role"], self.settings.jwt_secret, self.settings.jwt_hours)
        return {"token": token, "user": self.public_user(row)}

    def login(self, email: str, password: str) -> dict[str, Any]:
        row = self.db.one("SELECT * FROM users WHERE lower(email) = lower(?)", (email.strip(),))
        if not row or not verify_password(password, row["password_hash"]):
            raise ServiceError("Invalid email or password", 401)
        return self._session(row)

    def register(self, name: str, email: str, password: str, permit: str = "none") -> dict[str, Any]:
        name, email = name.strip(), email.strip().lower()
        if not name:
            raise ServiceError("Name is required")
        if not EMAIL_RE.match(email):
            raise ServiceError("Enter a valid email address")
        if len(password) < MIN_PASSWORD:
            raise ServiceError(f"Password must be at least {MIN_PASSWORD} characters")
        if permit not in PERMIT_TYPES:
            raise ServiceError(f"Unknown permit type. Choose one of: {', '.join(PERMIT_TYPES)}")
        if self.db.one("SELECT id FROM users WHERE lower(email) = ?", (email,)):
            raise ServiceError("An account with that email already exists", 409)
        user_id = f"u_{secrets.token_hex(4)}"
        role = "visitor" if permit == "none" else "student"
        self.db.execute(
            "INSERT INTO users (id, email, name, role, password_hash, permit) VALUES (?,?,?,?,?,?)",
            (user_id, email, name, role, hash_password(password), permit),
        )
        return self._session(self.get_user(user_id))

    def change_password(self, user_id: str, current: str, new: str) -> None:
        row = self.get_user(user_id)
        if not verify_password(current, row["password_hash"]):
            raise ServiceError("Current password is incorrect", 400)
        if len(new) < MIN_PASSWORD:
            raise ServiceError(f"Password must be at least {MIN_PASSWORD} characters")
        if current == new:
            raise ServiceError("New password must be different from the current one")
        self.db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new), user_id))

    def get_user(self, user_id: str) -> dict[str, Any]:
        row = self.db.one("SELECT * FROM users WHERE id = ?", (user_id,))
        if not row:
            raise ServiceError("User not found", 404)
        return row

    # ======================================================================
    # Profile (FR-15, FR-23 preference, FR-10 preferences)
    # ======================================================================
    @staticmethod
    def public_user(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"], "email": row["email"], "name": row["name"], "role": row["role"],
            "permit": row["permit"], "permit_label": PERMIT_TYPES.get(row["permit"], row["permit"]),
            "home": {"lat": row["home_lat"], "lng": row["home_lng"], "label": row["home_label"]}
            if row["home_lat"] is not None else None,
            "accessible_routing": bool(row["accessible_routing"]),
            "notifications": {
                "near_full": bool(row["notify_near_full"]), "full": bool(row["notify_full"]),
                "leave_by": bool(row["notify_leave_by"]),
                "quiet_start": row["quiet_start"], "quiet_end": row["quiet_end"],
            },
        }

    def update_profile(self, user_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        self.get_user(user_id)
        fields: dict[str, Any] = {}
        if changes.get("name") is not None:
            name = changes["name"].strip()
            if not name:
                raise ServiceError("Name can't be empty")
            fields["name"] = name
        if changes.get("permit") is not None:
            if changes["permit"] not in PERMIT_TYPES:
                raise ServiceError(f"Unknown permit type. Choose one of: {', '.join(PERMIT_TYPES)}")
            fields["permit"] = changes["permit"]
        if changes.get("home"):
            fields["home_lat"] = changes["home"]["lat"]
            fields["home_lng"] = changes["home"]["lng"]
            fields["home_label"] = changes["home"].get("label") or "Home"
        if changes.get("accessible_routing") is not None:
            fields["accessible_routing"] = int(bool(changes["accessible_routing"]))
        notif = changes.get("notifications") or {}
        for key, col in (("near_full", "notify_near_full"), ("full", "notify_full"), ("leave_by", "notify_leave_by")):
            if notif.get(key) is not None:
                fields[col] = int(bool(notif[key]))
        for key in ("quiet_start", "quiet_end"):
            if key in notif:
                val = notif[key]
                if val and not HM_RE.match(val):
                    raise ServiceError(f"{key} must be HH:MM (24-hour)")
                fields[key] = val or None
        if fields:
            sets = ", ".join(f"{k} = ?" for k in fields)
            self.db.execute(f"UPDATE users SET {sets} WHERE id = ?", (*fields.values(), user_id))
        return self.public_user(self.get_user(user_id))

    # ======================================================================
    # Campus data for the map (FR-3, FR-4 outlines, FR-22)
    # ======================================================================
    def meta(self) -> dict[str, Any]:
        """TR-69: the app shows a 'Simulated data' label when demo_mode is true."""
        return {
            "app": "UNT Smart Parking & Navigation",
            "version": "0.6.0",
            "milestone": "60%",
            "demo_mode": self.settings.demo_mode,
            "data_source": self.settings.data_source,
            "server_time": datetime.now().isoformat(timespec="seconds"),
        }

    @staticmethod
    def buildings() -> list[dict[str, Any]]:
        return BUILDINGS

    @staticmethod
    def lots() -> list[dict[str, Any]]:
        """Static lot info for drawing the map. Live availability is not built yet (FR-5)."""
        keys = ("id", "name", "kind", "lat", "lng", "polygon", "capacity", "accessible_spaces", "ev_chargers",
                "pay_by_hour", "hourly_rate")
        return [{k: lot[k] for k in keys} for lot in LOTS]

    @staticmethod
    def pois(category: str | None = None) -> list[dict[str, Any]]:
        if category and category not in POI_CATEGORIES:
            raise ServiceError(f"Unknown category. Choose one of: {', '.join(POI_CATEGORIES)}")
        return [p for p in POIS if not category or p["category"] == category]

    def events(self) -> list[dict[str, Any]]:
        """Seeded game days and closures. Not applied to lots yet (FR-19 is next milestone)."""
        rows = self.db.query("SELECT * FROM events ORDER BY start")
        for r in rows:
            r["lot_ids"] = json.loads(r["lot_ids"])
        return rows

    # ======================================================================
    # TODO (next milestone)
    # ----------------------------------------------------------------------
    # - Live availability + simulated feed (FR-5, FR-12, TR-60)
    # - Permit rules engine and lot filtering (FR-16 .. FR-19)
    # - Prediction model (FR-7, TR-70) and recommendations (FR-6, FR-11, FR-26)
    # - Drive / walk routing and building entrances (FR-8, FR-9, FR-21, FR-23)
    # - Building search (FR-20)
    # - Class schedule, leave-by, day planning (FR-2, FR-24, FR-25)
    # - Saved parking and favorites (FR-27, FR-28)
    # - Student reports (FR-13), alerts (FR-10)
    # - Parking administration (FR-14) and the demo control panel (TR-67)
    # - Offline bundle (FR-29)
    # ======================================================================
