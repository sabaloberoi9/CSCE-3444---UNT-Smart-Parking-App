"""Simulated demand patterns shared by the history generator and the live feed (TR-59, TR-60).

Everything here is SIMULATED. The goal is realistic *shape*: class-change peaks,
MWF vs TR differences, lighter Fridays, a busy first week, Thanksgiving, finals,
and football game days.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta

# Simulated Fall 2026 semester: 16 weeks (weeks 1-15 classes, week 16 finals)
SEMESTER_START = date(2026, 8, 17)  # a Monday
SEMESTER_WEEKS = 16
LABOR_DAY = date(2026, 9, 7)
THANKSGIVING_BREAK = {date(2026, 11, 25), date(2026, 11, 26), date(2026, 11, 27)}
# Simulated home football Saturdays (week numbers) with kickoff hour
GAME_WEEKS = {2: 18, 4: 14, 7: 18, 9: 14, 12: 15, 14: 14}


def week_of_semester(d: date) -> int:
    """1-based week number, clamped to 1..16 so any date still produces valid features."""
    w = (d - SEMESTER_START).days // 7 + 1
    return max(1, min(SEMESTER_WEEKS, w))


def is_holiday(d: date) -> bool:
    return d == LABOR_DAY or d in THANKSGIVING_BREAK


def game_kickoff(d: date) -> int | None:
    """Kickoff hour if d is a simulated home game Saturday, else None."""
    if d.weekday() != 5:
        return None
    raw_week = (d - SEMESTER_START).days // 7 + 1
    return GAME_WEEKS.get(raw_week)


def _smooth(hour: float, points: list[tuple[float, float]]) -> float:
    """Piecewise-linear interpolation over (hour, value) points."""
    for (h0, v0), (h1, v1) in zip(points, points[1:]):
        if h0 <= hour <= h1:
            t = (hour - h0) / (h1 - h0) if h1 > h0 else 0
            return v0 + t * (v1 - v0)
    return points[-1][1]


# Daily curves: fraction of peak demand by hour of day
_CURVES = {
    "commuter_mwf": [(0, .04), (6, .06), (7, .25), (8, .62), (9, .88), (10, .98), (11, 1.0), (13, .97),
                     (14, .85), (15, .70), (17, .50), (18, .42), (19, .35), (21, .18), (23, .06), (24, .04)],
    "commuter_tr": [(0, .04), (6, .05), (7, .20), (8, .50), (9, .80), (10, .95), (12, 1.0), (14, .96),
                    (15, .82), (17, .55), (18, .45), (19, .38), (21, .20), (23, .06), (24, .04)],
    "faculty": [(0, .05), (6, .08), (7, .35), (8, .75), (9, .92), (12, .95), (16, .85), (17, .55),
                (18, .25), (20, .10), (24, .05)],
    "resident": [(0, .92), (7, .90), (9, .78), (11, .66), (14, .64), (17, .75), (20, .86), (24, .92)],
    "visitor": [(0, .05), (8, .30), (10, .80), (12, .95), (14, .85), (17, .55), (20, .30), (24, .05)],
    "weekend": [(0, .06), (9, .10), (12, .18), (16, .16), (20, .12), (24, .06)],
}


def base_fraction(kind: str, attractiveness: float, dt: datetime, event_zone: bool = False) -> float:
    """Expected occupancy fraction (0..~1) for a lot at a moment, before noise."""
    d = dt.date()
    hour = dt.hour + dt.minute / 60
    dow = d.weekday()
    week = week_of_semester(d)

    if kind == "resident":
        frac = _smooth(hour, _CURVES["resident"]) * (0.95 if dow >= 5 else 1.0)
        return min(1.0, frac * attractiveness)

    if dow >= 5:
        frac = _smooth(hour, _CURVES["weekend"])
    elif kind == "faculty":
        frac = _smooth(hour, _CURVES["faculty"])
    elif kind == "visitor":
        frac = _smooth(hour, _CURVES["visitor"])
    else:
        curve = "commuter_tr" if dow in (1, 3) else "commuter_mwf"
        frac = _smooth(hour, _CURVES[curve])

    # Day-of-week and semester effects
    if dow == 4:
        frac *= 0.72  # lighter Fridays
    if week == 1:
        frac *= 1.12
    elif week == 2:
        frac *= 1.06
    elif 3 <= week <= 14:
        frac *= 0.995 ** (week - 3)  # attendance drifts down
    elif week == 15:
        frac *= 0.90
    elif week == 16:
        frac = frac * 0.78 + 0.05  # finals: flatter, lower
    if is_holiday(d):
        frac *= 0.22

    frac *= attractiveness
    if kind == "garage":
        frac *= 0.95
    if kind == "remote":
        frac *= 0.95

    # Game day surge
    kickoff = game_kickoff(d)
    if kickoff is not None:
        if event_zone and kickoff - 3 <= hour <= kickoff + 4:
            frac = max(frac, 0.97)
        elif kickoff - 2 <= hour <= kickoff + 3:
            frac += 0.12

    return max(0.0, min(1.02, frac))


def iter_times(start: datetime, end: datetime, step_minutes: int = 15):
    t = start
    step = timedelta(minutes=step_minutes)
    while t < end:
        yield t
        t += step


def logistic(x: float) -> float:
    return 1 / (1 + math.exp(-x))
