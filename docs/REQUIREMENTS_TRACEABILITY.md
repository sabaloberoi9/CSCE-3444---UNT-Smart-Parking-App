# Requirements traceability — 60% milestone

Status of each functional requirement in this build. Paths are relative to the repo root.

Status key: **Done** = built and tested · **Partial** = part of it is built · **Data only** = backend data
exists, no feature yet · **Not started**

| FR | Requirement | Status | Backend | Mobile | Tests |
|---|---|---|---|---|---|
| FR-1 | User Login | Done | `services/security.py`, `core.login/register/change_password`, `/auth/*` | `LoginScreen.tsx` (log in + create account), Profile → Password | `AuthTest`, `test_register_flow`, `test_requires_login` |
| FR-2 | Class Schedule Access | Data only | `classes` table seeded from `schedules.json` | — | `test_seed_counts` |
| FR-3 | Select Destination | Partial | `GET /buildings`, `GET /lots` | From / To selectors on the map | `test_campus_data` |
| FR-4 | Display Parking Lots | Partial | `GET /lots` (outlines, capacity) | Lot outlines colored by type | `test_buildings_and_lots` |
| FR-5 | Parking Availability | Not started | — | — | — |
| FR-6 | Recommend Best Parking Lot | Not started | — | Button placeholder (disabled) | — |
| FR-7 | Parking Prediction | Data only | `history.csv` generated | — | — |
| FR-8 | Navigation | Partial | — | Drive / Walk mode selector only | — |
| FR-9 | Walking Directions | Not started | Building entrances in `campus.py` | — | — |
| FR-10 | Parking Alerts | Partial | Alert preferences stored on the profile | Profile → Preferences | `test_update_permit_name_home_and_prefs` |
| FR-11 | Alternative Parking | Not started | — | — | — |
| FR-12 | Real-Time Parking Updates | Not started | — | — | — |
| FR-13 | Student Parking Feedback | Not started | `reports` table | — | — |
| FR-14 | Parking Administration | Not started | `lot_overrides`, `audit_log` tables | — | — |
| FR-15 | Permit Profile | Done | `core.update_profile`, `PATCH /me` | Profile → Parking pass | `ProfileTest`, `test_me_and_update` |
| FR-16 | Permit-Based Lot Filtering | Not started | Lot rules in `campus.py` | — | — |
| FR-17 | Time-Based Permit Rules | Data only | Lot rules in `campus.py` | — | — |
| FR-18 | No-Pass Options | Data only | Visitor / pay-by-hour lots in `campus.py` | — | — |
| FR-19 | Event and Game-Day Restrictions | Data only | `events` table seeded, `GET /events` | — | `test_events_seeded` |
| FR-20 | Building Search | Partial | — | Simple name / code filter in the place picker | — |
| FR-21 | Building Entrances | Data only | `campus.py` entrances | — | — |
| FR-22 | Campus Points of Interest | Data only | `campus.POIS`, `GET /pois` | — | `test_poi_filter` |
| FR-23 | Accessible Routing | Partial | Preference stored on the profile | Profile → Preferences | `test_update_permit_name_home_and_prefs` |
| FR-24 | Leave-By Alerts | Not started | — | — | — |
| FR-25 | Multi-Class Day Planning | Not started | — | — | — |
| FR-26 | Park-and-Walk Comparison | Not started | — | — | — |
| FR-27 | Save Parked Location | Not started | `saved_parking` table | — | — |
| FR-28 | Favorite Lots and Buildings | Data only | `favorites` table seeded | — | `test_seed_counts` |
| FR-29 | Offline Campus Map | Not started | — | — | — |

## Simulated data requirements

| TR | Status | Where |
|---|---|---|
| TR-58 simulation program, fixed seed | Done | `simulation/generate.py` (`SEED = 3444`) |
| TR-59 parking history | Done | `simulation/patterns.py`, `data/history.csv` |
| TR-60 live car entries and exits | Not started | — |
| TR-61 student reports incl. spam | Not started | Background accounts `u_sim01..20` are seeded |
| TR-62 test accounts | Done | `data/users.json` → `users` table |
| TR-63 class schedules | Done | `data/schedules.json` → `classes` table |
| TR-64 lots and permit rules | Done | `app/campus.py` |
| TR-65 events and closures | Done | `data/events.json` → `events` table |
| TR-66 simulated GPS | Partial | Home location presets on the Profile screen |
| TR-67 demo control panel | Not started | — |
| TR-68 same interfaces as real data | Partial | `DATA_SOURCE` setting |
| TR-69 "Simulated data" label | Done | `StatusBanner` in `Chrome.tsx`, `GET /meta` |
| TR-70 model testing | Not started | — |

## Future work (not planned for this course)

FW-1 Campus Shuttle Integration · FW-2 Sensor and Camera Counts · FW-3 Personalized Predictions ·
FW-4 Night Safe-Walk Routing · UNT single sign-on.
