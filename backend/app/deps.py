"""Shared FastAPI dependencies: the service instance and the logged-in user."""

from __future__ import annotations

from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.core import ParkingService, ServiceError
from app.services.security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_service(request: Request) -> ParkingService:
    return request.app.state.service


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    svc: ParkingService = Depends(get_service),
) -> dict[str, Any]:
    if creds is None:
        raise HTTPException(401, "Log in required")
    try:
        payload = decode_token(creds.credentials, svc.settings.jwt_secret)
        return svc.get_user(payload["sub"])
    except (jwt.PyJWTError, ServiceError, KeyError) as exc:
        raise HTTPException(401, "Session expired - please log in again") from exc


# TODO (next milestone): admin_user() guard for the parking administration endpoints (FR-14)
