"""UNT Smart Parking & Navigation API - 60% milestone build.

Built so far: database + seed data, user authentication, user profile, campus data
(buildings, lots, points of interest) for the map.
Not built yet: live availability, prediction, recommendations, routing, schedule,
alerts, reports, saved parking, admin and the demo control panel.

Run (from backend/):
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Interactive API docs: http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, campus, profile
from app.services.core import ParkingService, ServiceError


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = ParkingService(settings)
    # TODO (next milestone): background ticker for the simulated live feed and alerts (TR-24, TR-41)
    yield


app = FastAPI(
    title="UNT Smart Parking & Navigation API",
    version="0.6.0",
    description="CSCE 3444 project - 60% milestone. All data in demo mode is SIMULATED.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(ServiceError)
async def service_error(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


API_PREFIX = "/api/v1"  # TR-51: versioned API
for r in (auth.router, profile.router, campus.router):
    app.include_router(r, prefix=API_PREFIX)
