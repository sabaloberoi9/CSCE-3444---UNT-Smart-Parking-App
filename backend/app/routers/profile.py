"""User profile module (FR-15): name, parking pass, home location, accessibility and
notification preferences. Preferences are stored now; the features that use them
(accessible routing, alerts) come in the next milestone."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app import schemas
from app.deps import current_user, get_service
from app.services.core import ParkingService

router = APIRouter(tags=["profile"])


@router.get("/me")
def me(user: dict[str, Any] = Depends(current_user), svc: ParkingService = Depends(get_service)):
    return svc.public_user(user)


@router.patch("/me")
def update_me(body: schemas.ProfileIn, user=Depends(current_user), svc: ParkingService = Depends(get_service)):
    return svc.update_profile(user["id"], body.model_dump(exclude_unset=True))
