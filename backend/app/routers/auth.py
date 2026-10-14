"""User authentication module (FR-1).

Local accounts with hashed passwords and JWT login tokens. The token interface is kept
small so it can later be swapped for UNT single sign-on (see future work).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app import schemas
from app.deps import current_user, get_service
from app.services.core import ParkingService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: schemas.LoginIn, svc: ParkingService = Depends(get_service)):
    """Returns `{token, user}`. Send the token as `Authorization: Bearer <token>`."""
    return svc.login(body.email, body.password)


@router.post("/register", status_code=201)
def register(body: schemas.RegisterIn, svc: ParkingService = Depends(get_service)):
    """Create a local account and log in. Returns `{token, user}`."""
    return svc.register(body.name, body.email, body.password, body.permit)


@router.post("/change-password")
def change_password(body: schemas.ChangePasswordIn, user=Depends(current_user),
                    svc: ParkingService = Depends(get_service)):
    svc.change_password(user["id"], body.current_password, body.new_password)
    return {"ok": True}
