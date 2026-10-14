"""Request bodies for the API (validated by Pydantic)."""

from __future__ import annotations

from pydantic import BaseModel, Field


# -- authentication ------------------------------------------------------------
class LoginIn(BaseModel):
    email: str
    password: str


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    permit: str = "none"


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# -- profile -------------------------------------------------------------------
class Point(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    label: str | None = None


class NotificationPrefs(BaseModel):
    near_full: bool | None = None
    full: bool | None = None
    leave_by: bool | None = None
    quiet_start: str | None = None
    quiet_end: str | None = None


class ProfileIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    permit: str | None = None
    home: Point | None = None
    accessible_routing: bool | None = None
    notifications: NotificationPrefs | None = None


# TODO (next milestone): RecommendIn, DirectionsIn, ClassIn, SaveParkingIn, FavoriteIn, ReportIn, admin + demo bodies
