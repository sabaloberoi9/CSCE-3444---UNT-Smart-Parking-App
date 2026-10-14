"""SQLite storage for everything that changes: users, schedules, reports, notifications,
admin changes and events. Seeded from the simulated JSON files (TR-62, TR-63, TR-65).

SQLite keeps the class demo zero-setup. The SRS target is PostgreSQL + PostGIS; the
queries here are plain SQL so moving later is straightforward.

Milestone note (60%): the full schema is in place. Only `users` is read and written by the
API so far (auth + profile). `classes`, `favorites`, `events` are seeded and waiting for the
schedule, favorites and closure features; `saved_parking`, `reports`, `notifications`,
`lot_overrides` and `audit_log` are empty until those features are built.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from app.services.security import hash_password

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
    role TEXT NOT NULL, password_hash TEXT NOT NULL,
    permit TEXT NOT NULL DEFAULT 'none',
    home_lat REAL, home_lng REAL, home_label TEXT,
    accessible_routing INTEGER NOT NULL DEFAULT 0,
    notify_near_full INTEGER NOT NULL DEFAULT 1,
    notify_full INTEGER NOT NULL DEFAULT 1,
    notify_leave_by INTEGER NOT NULL DEFAULT 1,
    quiet_start TEXT, quiet_end TEXT,
    reliability REAL NOT NULL DEFAULT 0.7
);
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, course TEXT NOT NULL,
    title TEXT, building_id TEXT NOT NULL, room TEXT, days TEXT NOT NULL,
    start TEXT NOT NULL, "end" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS favorites (
    user_id TEXT NOT NULL, kind TEXT NOT NULL, item_id TEXT NOT NULL,
    PRIMARY KEY (user_id, kind, item_id)
);
CREATE TABLE IF NOT EXISTS saved_parking (
    user_id TEXT PRIMARY KEY, lot_id TEXT, lat REAL NOT NULL, lng REAL NOT NULL,
    level TEXT, row_label TEXT, note TEXT, saved_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, lot_id TEXT NOT NULL,
    kind TEXT NOT NULL, created_at TEXT NOT NULL, weight REAL NOT NULL, accepted INTEGER NOT NULL,
    reason TEXT
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, kind TEXT NOT NULL,
    title TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL, dedupe_key TEXT,
    read INTEGER NOT NULL DEFAULT 0, data TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL, start TEXT NOT NULL,
    "end" TEXT NOT NULL, lot_ids TEXT NOT NULL, effect TEXT NOT NULL, created_by TEXT
);
CREATE TABLE IF NOT EXISTS lot_overrides (
    lot_id TEXT PRIMARY KEY, capacity INTEGER, note TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id TEXT NOT NULL, action TEXT NOT NULL,
    details TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reports_lot ON reports(lot_id, created_at);
CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id, created_at);
"""

TABLES = ("users", "classes", "favorites", "saved_parking", "reports", "notifications", "events",
          "lot_overrides", "audit_log")


class Database:
    def __init__(self, path: Path | str) -> None:
        self.path = str(path)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    # -- low level ---------------------------------------------------------
    def execute(self, sql: str, params: tuple | dict = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.execute(sql, params)
            self.conn.commit()
            return cur

    def query(self, sql: str, params: tuple | dict = ()) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def one(self, sql: str, params: tuple | dict = ()) -> dict[str, Any] | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    # -- seeding -------------------------------------------------------------
    def reset_and_seed(self, data_dir: Path) -> None:
        with self._lock:
            for table in TABLES:
                self.conn.execute(f"DELETE FROM {table}")
            self.conn.commit()
        self.seed(data_dir)

    def counts(self) -> dict[str, int]:
        """Row count per table (used by the seed script and tests)."""
        return {t: self.one(f"SELECT COUNT(*) AS n FROM {t}")["n"] for t in TABLES}  # type: ignore[index]

    def seed(self, data_dir: Path) -> None:
        if self.one("SELECT id FROM users LIMIT 1"):
            return
        users = json.loads((data_dir / "users.json").read_text())
        schedules = json.loads((data_dir / "schedules.json").read_text())
        events = json.loads((data_dir / "events.json").read_text())
        with self._lock:
            for u in users:
                home = u.get("home") or {}
                self.conn.execute(
                    "INSERT INTO users (id, email, name, role, password_hash, permit, home_lat, home_lng, home_label)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (u["id"], u["email"], u["name"], u["role"], hash_password(u["password"]), u["permit"],
                     home.get("lat"), home.get("lng"), home.get("label")),
                )
            for user_id, classes in schedules.items():
                for c in classes:
                    self.conn.execute(
                        'INSERT INTO classes (user_id, course, title, building_id, room, days, start, "end")'
                        " VALUES (?,?,?,?,?,?,?,?)",
                        (user_id, c["course"], c.get("title"), c["building_id"], c.get("room"), c["days"],
                         c["start"], c["end"]),
                    )
            for e in events:
                self.conn.execute(
                    'INSERT INTO events (id, type, title, start, "end", lot_ids, effect, created_by)'
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (e["id"], e["type"], e["title"], e["start"], e["end"], json.dumps(e["lot_ids"]),
                     e["effect"], "simulation"),
                )
            # Starter favorites so alerts can be demoed right away
            for fav in [("u_alex", "lot", "welch_lot"), ("u_alex", "lot", "dp_lot"),
                        ("u_alex", "building", "gab"), ("u_sam", "lot", "highland_garage")]:
                self.conn.execute("INSERT OR IGNORE INTO favorites VALUES (?,?,?)", fav)
            self.conn.commit()
