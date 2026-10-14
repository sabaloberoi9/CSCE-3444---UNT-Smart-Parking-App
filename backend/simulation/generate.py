"""Generate all simulated data for testing and demos (TR-58 .. TR-65).

Run from the backend folder:
    python -m simulation.generate

Outputs (in backend/data/):
    history.csv      15-minute occupancy for every lot across a 16-week semester
    users.json       made-up test accounts (no real student information)
    schedules.json   made-up class schedules
    events.json      game days, graduation, maintenance and closure scenarios

A fixed seed makes every run produce identical data (TR-58).
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.campus import LOTS  # noqa: E402
from simulation.patterns import (  # noqa: E402
    GAME_WEEKS,
    SEMESTER_START,
    SEMESTER_WEEKS,
    base_fraction,
    iter_times,
)

SEED = 3444
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEMO_PASSWORD = "demo1234"


def generate_history(rng: np.random.Generator) -> int:
    start = datetime.combine(SEMESTER_START, datetime.min.time())
    end = start + timedelta(weeks=SEMESTER_WEEKS)
    path = DATA_DIR / "history.csv"
    rows = 0
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lot_id", "timestamp", "occupied", "capacity"])
        for lot in LOTS:
            ar = 0.0  # AR(1) noise so neighboring intervals are correlated
            for t in iter_times(start, end, 15):
                ar = 0.93 * ar + rng.normal(0, 0.012)
                frac = base_fraction(lot["kind"], lot["attractiveness"], t, lot["event_zone"])
                frac = frac + ar + rng.normal(0, 0.01)
                occupied = int(round(np.clip(frac, 0, 1) * lot["capacity"]))
                w.writerow([lot["id"], t.isoformat(timespec="minutes"), occupied, lot["capacity"]])
                rows += 1
    return rows


def generate_users() -> list[dict]:
    users = [
        {"id": "u_alex", "email": "alex.commuter@demo.local", "name": "Alex Rivera", "role": "student",
         "permit": "commuter", "home": {"lat": 33.1850, "lng": -97.1150, "label": "Apartment (South Denton)"}},
        {"id": "u_riley", "email": "riley.resident@demo.local", "name": "Riley Chen", "role": "student",
         "permit": "resident", "home": {"lat": 33.2046, "lng": -97.1559, "label": "Mean Green Village"}},
        {"id": "u_morgan", "email": "morgan.faculty@demo.local", "name": "Dr. Jordan Morgan", "role": "student",
         "permit": "faculty_staff", "home": {"lat": 33.2300, "lng": -97.1000, "label": "Home"}},
        {"id": "u_sam", "email": "sam.garage@demo.local", "name": "Sam Patel", "role": "student",
         "permit": "garage", "home": {"lat": 33.1700, "lng": -97.0900, "label": "Home (Corinth)"}},
        {"id": "u_casey", "email": "casey.visitor@demo.local", "name": "Casey Brooks", "role": "visitor",
         "permit": "none", "home": {"lat": 33.2200, "lng": -97.1300, "label": "Hotel"}},
        {"id": "u_pat", "email": "pat.admin@demo.local", "name": "Pat Admin", "role": "admin",
         "permit": "faculty_staff", "home": {"lat": 33.2150, "lng": -97.1200, "label": "Home"}},
    ]
    # Background users who submit simulated reports (TR-61)
    for i in range(1, 21):
        users.append({"id": f"u_sim{i:02d}", "email": f"sim{i:02d}@demo.local", "name": f"Sim Student {i}",
                      "role": "student", "permit": "commuter",
                      "home": {"lat": 33.19 + i * 0.001, "lng": -97.12, "label": "Home"}})
    for u in users:
        u["password"] = DEMO_PASSWORD
    return users


def generate_schedules() -> dict[str, list[dict]]:
    """Includes back-to-back classes far apart (GAB -> Discovery Park) for FR-25 warnings."""
    return {
        "u_alex": [
            {"course": "CSCE 3444", "title": "Software Engineering", "building_id": "dp", "room": "B185",
             "days": "MW", "start": "11:30", "end": "12:50"},
            {"course": "MATH 2700", "title": "Linear Algebra", "building_id": "gab", "room": "310",
             "days": "MWF", "start": "09:00", "end": "09:50"},
            {"course": "PSCI 1040", "title": "American Government", "building_id": "lang", "room": "117",
             "days": "MWF", "start": "10:00", "end": "10:50"},
            {"course": "TECM 2700", "title": "Technical Writing", "building_id": "gab", "room": "105",
             "days": "TR", "start": "10:00", "end": "11:20"},
            {"course": "CSCE 3600", "title": "Systems Programming", "building_id": "dp", "room": "B142",
             "days": "TR", "start": "11:30", "end": "12:50"},
        ],
        "u_riley": [
            {"course": "BIOL 1710", "title": "Biology I", "building_id": "lsc", "room": "A120",
             "days": "MWF", "start": "08:00", "end": "08:50"},
            {"course": "CHEM 1410", "title": "General Chemistry", "building_id": "chem", "room": "109",
             "days": "TR", "start": "09:30", "end": "10:50"},
        ],
        "u_sam": [
            {"course": "BCIS 3610", "title": "Business Information Systems", "building_id": "blb", "room": "055",
             "days": "MW", "start": "13:00", "end": "14:20"},
            {"course": "MUCP 1180", "title": "Music Appreciation", "building_id": "music", "room": "232",
             "days": "MW", "start": "14:30", "end": "15:50"},
        ],
    }


def generate_events() -> list[dict]:
    events = []
    for week, kickoff in GAME_WEEKS.items():
        d = SEMESTER_START + timedelta(weeks=week - 1, days=5)
        events.append({
            "id": f"game_w{week}", "type": "game_day", "title": "Mean Green Football Home Game",
            "start": datetime(d.year, d.month, d.day, kickoff - 4).isoformat(timespec="minutes"),
            "end": datetime(d.year, d.month, d.day, min(23, kickoff + 4)).isoformat(timespec="minutes"),
            "lot_ids": ["coliseum_lot", "stadium_lot", "union_circle_garage"],
            "effect": "reserved",
        })
    events.append({
        "id": "graduation_fall", "type": "graduation", "title": "Fall Commencement",
        "start": "2026-12-11T08:00", "end": "2026-12-11T17:00",
        "lot_ids": ["coliseum_lot", "union_circle_garage"], "effect": "reserved",
    })
    events.append({
        "id": "maint_maple", "type": "maintenance", "title": "Maple Street Lot restriping",
        "start": "2026-10-03T06:00", "end": "2026-10-04T20:00",
        "lot_ids": ["maple_lot"], "effect": "closed",
    })
    return events


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    rows = generate_history(rng)
    (DATA_DIR / "users.json").write_text(json.dumps(generate_users(), indent=2))
    (DATA_DIR / "schedules.json").write_text(json.dumps(generate_schedules(), indent=2))
    (DATA_DIR / "events.json").write_text(json.dumps(generate_events(), indent=2))
    print(f"history.csv: {rows:,} rows across {len(LOTS)} lots ({SEMESTER_WEEKS} weeks, 15-min intervals)")
    print("users.json, schedules.json, events.json written to", DATA_DIR)
    print(f"All demo accounts use password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
