"""Public campus data for the map and the navigation selectors."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.campus import PERMIT_TYPES
from app.deps import get_service
from app.services.core import ParkingService

router = APIRouter(tags=["campus"])


@router.get("/meta")
def meta(svc: ParkingService = Depends(get_service)):
    return svc.meta()


@router.get("/permit-types")
def permit_types():
    return PERMIT_TYPES


@router.get("/buildings")
def buildings(svc: ParkingService = Depends(get_service)):
    """FR-3: destinations for the navigation selectors."""
    return svc.buildings()


@router.get("/lots")
def lots(svc: ParkingService = Depends(get_service)):
    """FR-4: lot outlines and static details. Live availability (FR-5) is not built yet."""
    return svc.lots()


@router.get("/pois")
def pois(category: str | None = None, svc: ParkingService = Depends(get_service)):
    """FR-22 (data only - not on the map yet)"""
    return svc.pois(category)


@router.get("/events")
def events(svc: ParkingService = Depends(get_service)):
    """Seeded game days and closures (FR-19 rules not applied yet)."""
    return svc.events()


# TODO (next milestone): /lots/{id}/availability, /lots/{id}/prediction, /lots/{id}/forecast,
# /lots/no-pass-options, /search, /bundle, /model/metrics
