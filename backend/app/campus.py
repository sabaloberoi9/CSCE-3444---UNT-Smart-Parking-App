"""Campus base data: buildings, entrances, parking lots, permit rules, points of interest.

IMPORTANT (TR-64, TR-47): Building positions and lot outlines come from OpenStreetMap
(© OpenStreetMap contributors, ODbL; fetched 2026-09-16), so they sit on the real
campus. Each app lot is mapped to one real UNT lot (the official lot number is noted
next to its outline). Building entrances are still generated offsets, and every
capacity, permit assignment and rule is SIMULATED. Before a real release the team must
walk the entrances and replace simulated rules with UNT Transportation Services' rules.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Permit types (FR-15)
# ---------------------------------------------------------------------------
PERMIT_TYPES: dict[str, str] = {
    "commuter": "Commuter Student",
    "resident": "Resident Student",
    "faculty_staff": "Faculty / Staff",
    "garage": "Garage Permit",
    "none": "No Pass / Visitor",
}

# Special tokens used inside lot rules
ANY_PERMIT = "any_permit"  # any UNT permit holder (not "none")
PUBLIC = "public"          # anyone, including no pass

WEEKDAYS = [0, 1, 2, 3, 4]
WEEKEND = [5, 6]
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]


def _rect(lat: float, lng: float, dlat: float = 0.0007, dlng: float = 0.0009) -> list[list[float]]:
    """Small rectangle polygon around a center point, as [lat, lng] pairs (fallback for lots without an outline)."""
    return [
        [lat - dlat / 2, lng - dlng / 2],
        [lat - dlat / 2, lng + dlng / 2],
        [lat + dlat / 2, lng + dlng / 2],
        [lat + dlat / 2, lng - dlng / 2],
    ]


def _centroid(poly: list[list[float]]) -> tuple[float, float]:
    """Area-weighted centre of a [lat, lng] ring."""
    a = cx = cy = 0.0
    for i, (y1, x1) in enumerate(poly):
        y2, x2 = poly[(i + 1) % len(poly)]
        cross = x1 * y2 - x2 * y1
        a += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(a) < 1e-12:
        return poly[0][0], poly[0][1]
    return round(cy / (3 * a), 5), round(cx / (3 * a), 5)


# Real lot outlines (FR-4), simplified to about 3 m, as [lat, lng] rings.
# Source: OpenStreetMap, © OpenStreetMap contributors (ODbL). Way ids are given for re-fetching.
LOT_OUTLINES: dict[str, list[list[float]]] = {
    # Highland Street Parking Garage (OSM way 256780366)
    "highland_garage": [[33.20921, -97.14606], [33.2092, -97.14546], [33.20839, -97.14546], [33.2084, -97.14607], [33.20901, -97.14606], [33.20899, -97.14615], [33.20914, -97.14615], [33.20913, -97.14606]],
    # Union Circle Garage (OSM way 257710002)
    "union_circle_garage": [[33.21139, -97.14505], [33.21138, -97.14451], [33.21055, -97.14452], [33.21056, -97.14522], [33.211, -97.14521], [33.211, -97.14505]],
    # Lot 27 (OSM way 257709987)
    "coliseum_lot": [[33.20842, -97.15221], [33.2086, -97.15176], [33.20887, -97.15135], [33.20927, -97.15134], [33.20929, -97.15232], [33.20924, -97.15233], [33.20924, -97.15279], [33.20849, -97.1528], [33.20852, -97.15273], [33.20847, -97.15273], [33.20846, -97.15263], [33.20851, -97.15244], [33.20844, -97.15234]],
    # Lot 80 (OSM way 517776428)
    "stadium_lot": [[33.20162, -97.15696], [33.20064, -97.15697], [33.20027, -97.15724], [33.1998, -97.15807], [33.19972, -97.15861], [33.20162, -97.15856]],
    # Lot 23 (OSM way 260409851)
    "maple_lot": [[33.20753, -97.14988], [33.2072, -97.14989], [33.20721, -97.15057], [33.20686, -97.15057], [33.20685, -97.14921], [33.20692, -97.14921], [33.20692, -97.1491], [33.20684, -97.1491], [33.20684, -97.14869], [33.20745, -97.14869], [33.20746, -97.14922], [33.20735, -97.14922], [33.20735, -97.14937], [33.20753, -97.14937]],
    # Lot 11 (OSM way 260225250)
    "welch_lot": [[33.21458, -97.15222], [33.21458, -97.15271], [33.21453, -97.15271], [33.21453, -97.15276], [33.21385, -97.15277], [33.21385, -97.1525], [33.21379, -97.1525], [33.21379, -97.15195], [33.21387, -97.15195], [33.21387, -97.15188], [33.21408, -97.15188], [33.21408, -97.15195], [33.21438, -97.15195], [33.21437, -97.15219]],
    # Lot 26 (OSM way 257710000)
    "chestnut_lot": [[33.2103, -97.15275], [33.2103, -97.15226], [33.21019, -97.15227], [33.21018, -97.15214], [33.21034, -97.15214], [33.21034, -97.15152], [33.20952, -97.15153], [33.20952, -97.15214], [33.21006, -97.15213], [33.21006, -97.15223], [33.20985, -97.15224], [33.20985, -97.15275]],
    # Lot 50 (OSM way 293804598)
    "sage_fac_lot": [[33.21163, -97.14522], [33.21162, -97.14448], [33.21252, -97.14447], [33.21252, -97.14475], [33.21256, -97.1448], [33.21252, -97.14521]],
    # Lot 35 (OSM way 517786207)
    "mgv_resident_lot": [[33.20546, -97.15627], [33.20477, -97.1547], [33.20448, -97.15489], [33.20512, -97.15647]],
    # Lot 9 (OSM way 196948636)
    "bruce_resident_lot": [[33.2136, -97.15048], [33.2136, -97.14999], [33.21355, -97.14999], [33.21354, -97.14988], [33.21324, -97.14988], [33.21324, -97.14994], [33.21319, -97.14994], [33.21319, -97.15006], [33.21307, -97.14997], [33.21307, -97.14988], [33.21283, -97.14988], [33.21283, -97.14994], [33.21278, -97.14994], [33.21278, -97.15049], [33.21284, -97.15049], [33.21285, -97.15056], [33.21355, -97.15056], [33.21356, -97.15049]],
    # Union Circle Parking (OSM way 293804761)
    "union_visitor_lot": [[33.21141, -97.14603], [33.21142, -97.14555], [33.21136, -97.14555], [33.21136, -97.14549], [33.21114, -97.14549], [33.21113, -97.14556], [33.21098, -97.14556], [33.21098, -97.1461], [33.21135, -97.1461], [33.21135, -97.14603]],
    # Lot 93 (OSM way 197059045)
    "dp_lot": [[33.2546, -97.15058], [33.25376, -97.14897], [33.2536, -97.14901], [33.25302, -97.14944], [33.25388, -97.1511]],
}


def _entrances(lat: float, lng: float, accessible_side: str = "south") -> list[dict[str, Any]]:
    off = 0.00018
    sides = {
        "north": (lat + off, lng),
        "south": (lat - off, lng),
        "east": (lat, lng + off * 1.2),
        "west": (lat, lng - off * 1.2),
    }
    out = []
    for side, (la, ln) in sides.items():
        if side in ("north", "south", accessible_side):
            out.append({
                "name": f"{side.capitalize()} Entrance",
                "lat": round(la, 6),
                "lng": round(ln, 6),
                "accessible": side == accessible_side,
            })
    return out


# ---------------------------------------------------------------------------
# Buildings (FR-3, FR-20, FR-21, FR-23)
# ---------------------------------------------------------------------------
_BUILDINGS_RAW = [
    # id, name, code, aliases, lat, lng (OSM building centre), accessible side
    ("union", "University Union", "UNION", ["union", "student union"], 33.21064, -97.14729, "south"),
    ("willis", "Willis Library", "LIB", ["library", "willis"], 33.21012, -97.14901, "east"),
    ("gab", "General Academic Building", "GAB", ["general academic"], 33.21319, -97.14815, "west"),
    ("blb", "Business Leadership Building", "BLB", ["business", "cob"], 33.20887, -97.1477, "north"),
    ("lsc", "Life Sciences Complex", "LSC", ["life sciences", "biology"], 33.21215, -97.14903, "south"),
    ("env", "Environmental Science Building", "ENV", ["env sci", "environmental"], 33.21416, -97.15139, "east"),
    ("music", "Music Building", "MU", ["music", "college of music"], 33.21068, -97.15003, "west"),
    ("chem", "Chemistry Building", "CHEM", ["chemistry"], 33.21404, -97.14998, "north"),
    ("lang", "Language Building", "LANG", ["language", "languages"], 33.21406, -97.14665, "south"),
    ("sage", "Sage Hall", "SAGE", ["sage"], 33.21211, -97.14674, "south"),
    ("wooten", "Wooten Hall", "WH", ["wooten"], 33.20986, -97.14568, "east"),
    ("hurley", "Hurley Administration Building", "HUR", ["admin", "administration", "hurley"], 33.21116, -97.14848, "north"),
    ("pohl", "Pohl Recreation Center", "PRC", ["rec center", "gym", "pohl"], 33.21207, -97.15404, "east"),
    ("coliseum", "UNT Coliseum", "COL", ["super pit", "coliseum", "arena"], 33.20867, -97.15407, "north"),
    ("stadium", "DATCU Stadium", "STAD", ["football stadium", "stadium"], 33.20419, -97.15942, "north"),
    ("dp", "Discovery Park", "DP", ["discovery park", "engineering", "csce"], 33.25394, -97.15276, "south"),
]

BUILDINGS: list[dict[str, Any]] = [
    {
        "id": bid,
        "name": name,
        "code": code,
        "aliases": aliases,
        "lat": lat,
        "lng": lng,
        "entrances": _entrances(lat, lng, acc),
    }
    for bid, name, code, aliases, lat, lng, acc in _BUILDINGS_RAW
]

# ---------------------------------------------------------------------------
# Parking lots (FR-4, FR-5, FR-16, FR-17, FR-18) - capacities and rules SIMULATED
# kind: commuter | resident | faculty | garage | visitor | remote
# ---------------------------------------------------------------------------
ENFORCED = {"start": "07:00", "end": "19:00"}


def _std_rules(primary: list[str], open_after_hours: bool = True) -> list[dict[str, Any]]:
    """Primary permits during enforcement; optionally open to any permit / public after hours."""
    rules = [{"permits": primary, "days": WEEKDAYS, **ENFORCED}]
    if open_after_hours:
        rules += [
            {"permits": [ANY_PERMIT, PUBLIC], "days": WEEKDAYS, "start": "19:00", "end": "23:59"},
            {"permits": [ANY_PERMIT, PUBLIC], "days": WEEKDAYS, "start": "00:00", "end": "07:00"},
            {"permits": [ANY_PERMIT, PUBLIC], "days": WEEKEND, "start": "00:00", "end": "23:59"},
        ]
    return rules


_LOTS_RAW = [
    # id, name, kind, lat, lng (overridden by the outline centroid when LOT_OUTLINES has the lot),
    # capacity, attractiveness, accessible spaces, ev, pay_by_hour, rate, rules
    ("highland_garage", "Highland Street Garage", "garage", 33.2121, -97.1458, 900, 1.00, 20, 8, True, 2.50,
     [{"permits": ["garage", "faculty_staff"], "days": ALL_DAYS, "start": "00:00", "end": "23:59"}]),
    ("union_circle_garage", "Union Circle Garage", "garage", 33.2059, -97.1560, 1000, 0.92, 22, 10, True, 2.50,
     [{"permits": ["garage", "faculty_staff"], "days": ALL_DAYS, "start": "00:00", "end": "23:59"}]),
    ("coliseum_lot", "Coliseum Lot", "commuter", 33.2069, -97.1590, 650, 0.95, 14, 0, False, None,
     _std_rules(["commuter"])),
    ("stadium_lot", "Stadium Lot", "remote", 33.2025, -97.1615, 1200, 0.62, 18, 4, False, None,
     _std_rules(["commuter", "resident"])),
    ("maple_lot", "Maple Street Lot", "commuter", 33.2080, -97.1452, 280, 1.03, 8, 0, False, None,
     _std_rules(["commuter"])),
    ("welch_lot", "Welch Street Lot", "commuter", 33.2138, -97.1520, 320, 1.02, 8, 2, False, None,
     _std_rules(["commuter"])),
    ("chestnut_lot", "Chestnut Street Lot", "faculty", 33.2100, -97.1510, 180, 0.98, 6, 2, False, None,
     _std_rules(["faculty_staff"])),
    ("sage_fac_lot", "Sage Hall Faculty Lot", "faculty", 33.2140, -97.1470, 120, 0.97, 5, 0, False, None,
     _std_rules(["faculty_staff"])),
    ("mgv_resident_lot", "Mean Green Village Lot", "resident", 33.2060, -97.1530, 400, 0.90, 10, 0, False, None,
     [{"permits": ["resident"], "days": ALL_DAYS, "start": "00:00", "end": "23:59"}]),
    ("bruce_resident_lot", "Bruce Hall Resident Lot", "resident", 33.2096, -97.1440, 220, 0.93, 6, 0, False, None,
     [{"permits": ["resident"], "days": ALL_DAYS, "start": "00:00", "end": "23:59"}]),
    ("union_visitor_lot", "Union Visitor Lot", "visitor", 33.2116, -97.1482, 90, 1.00, 4, 2, True, 3.00,
     []),  # pay-by-hour for everyone
    ("dp_lot", "Discovery Park Lot", "commuter", 33.2548, -97.1510, 700, 0.80, 16, 6, False, None,
     _std_rules(["commuter", "faculty_staff", "resident"])),
]


def _lot_geometry(lid: str, kind: str, lat: float, lng: float) -> tuple[float, float, list[list[float]]]:
    outline = LOT_OUTLINES.get(lid)
    if outline:
        clat, clng = _centroid(outline)
        return clat, clng, outline
    big = kind in ("garage", "remote")
    return lat, lng, _rect(lat, lng, 0.0012 if big else 0.0008, 0.0014 if big else 0.0010)


LOTS: list[dict[str, Any]] = [
    {
        "id": lid,
        "name": name,
        "kind": kind,
        "lat": geo[0],
        "lng": geo[1],
        "polygon": geo[2],
        "capacity": cap,
        "attractiveness": attr,
        "accessible_spaces": acc,
        "ev_chargers": ev,
        "pay_by_hour": pay,
        "hourly_rate": rate,
        "rules": rules,
        "event_zone": lid in ("coliseum_lot", "stadium_lot", "union_circle_garage"),
    }
    for lid, name, kind, lat, lng, cap, attr, acc, ev, pay, rate, rules in _LOTS_RAW
    for geo in [_lot_geometry(lid, kind, lat, lng)]
]

# ---------------------------------------------------------------------------
# Points of interest (FR-22)
# ---------------------------------------------------------------------------
POIS: list[dict[str, Any]] = [
    {"id": "poi_union_food", "name": "Union Food Court", "category": "dining", "lat": 33.2112, "lng": -97.1472},
    {"id": "poi_champs", "name": "Champs Dining Hall", "category": "dining", "lat": 33.2062, "lng": -97.1522},
    {"id": "poi_kerr", "name": "Kerr Dining Hall", "category": "dining", "lat": 33.2077, "lng": -97.1475},
    {"id": "poi_willis", "name": "Willis Library", "category": "library", "lat": 33.2104, "lng": -97.1488},
    {"id": "poi_dp_library", "name": "Discovery Park Library", "category": "library", "lat": 33.2538, "lng": -97.1520},
    {"id": "poi_advising", "name": "Advising Center", "category": "advising", "lat": 33.2095, "lng": -97.1497},
    {"id": "poi_bus_union", "name": "Union Bus Stop", "category": "bus_stop", "lat": 33.2107, "lng": -97.1461},
    {"id": "poi_bus_coliseum", "name": "Coliseum Bus Stop", "category": "bus_stop", "lat": 33.2083, "lng": -97.1553},
    {"id": "poi_bus_dp", "name": "Discovery Park Bus Stop", "category": "bus_stop", "lat": 33.2542, "lng": -97.1530},
    {"id": "poi_bike_gab", "name": "GAB Bike Racks", "category": "bike_rack", "lat": 33.2125, "lng": -97.1495},
    {"id": "poi_bike_union", "name": "Union Bike Racks", "category": "bike_rack", "lat": 33.2106, "lng": -97.1476},
    {"id": "poi_ev_highland", "name": "Highland Garage EV Chargers", "category": "ev_charging", "lat": 33.2088, "lng": -97.1462},
    {"id": "poi_ev_ucg", "name": "Union Circle Garage EV Chargers", "category": "ev_charging", "lat": 33.2109, "lng": -97.1453},
]

POI_CATEGORIES = ["dining", "library", "advising", "bus_stop", "bike_rack", "ev_charging"]

BUILDINGS_BY_ID = {b["id"]: b for b in BUILDINGS}
LOTS_BY_ID = {lot["id"]: lot for lot in LOTS}
