# UNT Smart Parking & Navigation — Test Build

CSCE 3444 team project. This folder is the in-progress (about 60%) version of the app. The finished
build lives separately in `unt-parking-app/` next to this folder and is not changed by anything here.

## What's done

| Module | Status | Where |
|---|---|---|
| Database (SQLite, full schema for every feature) | Done | `backend/app/services/db.py` |
| Simulated seed data (accounts, class schedules, events, 16-week parking history) | Done | `backend/simulation/generate.py`, `backend/data/` |
| Database seeding script | Done | `backend/simulation/seed_db.py` |
| User authentication: log in, create account, change password, JWT sessions, hashed passwords | Done | `backend/app/routers/auth.py`, `mobile/src/screens/LoginScreen.tsx` |
| User profile: name, parking pass, home, accessibility and alert preferences | Done | `backend/app/routers/profile.py`, `mobile/src/screens/ProfileScreen.tsx` |
| Campus data API (buildings, lot outlines, points of interest, events) | Done | `backend/app/routers/campus.py`, `backend/app/campus.py` |
| Campus map (buildings, lots colored by type, legend) | Partial | `mobile/src/screens/MapScreen.tsx` |
| Navigation selectors (From / To, swap, Drive / Walk, pick from list or tap the map) | UI only | `mobile/src/screens/MapScreen.tsx`, `mobile/src/components/PlacePicker.tsx` |

## What's left (next milestone)

Live lot availability and the simulated live feed, the parking prediction model, parking
recommendations, drive and walking directions, building search, permit-based lot filtering,
class schedule and leave-by times, saved parking, favorites, student reports, alerts, parking
administration, the demo control panel and the offline map. The "Find parking & directions"
button on the map is disabled until those are built. See `docs/REQUIREMENTS_TRACEABILITY.md`.

## Run it

**Backend** (Python 3.10+), from `backend/`:

```bash
./setup.sh                     # venv, packages, seed data, database
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs. Reset the database any time with
`python -m simulation.seed_db --reset`. Run the tests with `python -m pytest`.

**Mobile app** (Expo SDK 57), from `mobile/`:

```bash
npm install
npx expo start
```

Open it in Expo Go on a phone on the same Wi-Fi as the computer running the backend. If the app
can't reach the server, set `EXPO_PUBLIC_API_URL` (see `mobile/.env.example`).

## Demo accounts

Password `demo1234`: alex.commuter, riley.resident, morgan.faculty, sam.garage, casey.visitor,
pat.admin (all `@demo.local`). You can also create a new account from the login screen.

All parking data is simulated. Building and lot positions follow UNT Denton; coordinates are approximate.
