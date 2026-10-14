"""Password hashing and login tokens (TR-2, TR-3).

Demo login uses local test accounts. The token interface is kept small so it can
later be swapped for UNT single sign-on (OpenID Connect / SAML) - see future work.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"pbkdf2${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


def create_token(user_id: str, role: str, secret: str, hours: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "role": role, "iat": now, "exp": now + timedelta(hours=hours)}
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str, secret: str) -> dict:
    """Raises jwt.PyJWTError if the token is invalid or expired."""
    return jwt.decode(token, secret, algorithms=["HS256"])
