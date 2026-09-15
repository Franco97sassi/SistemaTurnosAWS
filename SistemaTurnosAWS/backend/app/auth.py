import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field


Role = Literal["operador", "admin"]
bearer_scheme = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class UserIdentity(BaseModel):
    email: str
    name: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserIdentity


def _settings() -> tuple[str, str, str, str, int]:
    secret = os.getenv("JWT_SECRET", "local-development-secret-change-me")
    email = os.getenv("ADMIN_EMAIL", "admin@turnos.local").strip().lower()
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
    password = os.getenv("ADMIN_PASSWORD", "TurnosDemo2026!")
    ttl = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    return secret, email, password_hash, password, ttl


def _verify_password(password: str, expected_hash: str, fallback_password: str) -> bool:
    if not expected_hash:
        return hmac.compare_digest(password, fallback_password)
    try:
        algorithm, iterations, salt, digest = expected_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
        ).hex()
        return hmac.compare_digest(candidate, digest)
    except (TypeError, ValueError):
        return False


def authenticate(credentials: LoginRequest) -> TokenResponse:
    secret, expected_email, password_hash, fallback_password, ttl = _settings()
    if not (
        hmac.compare_digest(credentials.email.strip().lower(), expected_email)
        and _verify_password(credentials.password, password_hash, fallback_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(timezone.utc)
    user = UserIdentity(email=expected_email, name="Equipo de recepción", role="admin")
    token = _encode_token(
        {
            "sub": user.email,
            "name": user.name,
            "role": user.role,
            "iat": now,
            "exp": now + timedelta(minutes=ttl),
            "iss": "turnos-api",
        },
        secret,
    )
    return TokenResponse(access_token=token, expires_in=ttl * 60, user=user)


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> UserIdentity:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"},
        )
    secret, *_ = _settings()
    try:
        payload = _decode_token(credentials.credentials, secret)
        return UserIdentity(
            email=payload["sub"],
            name=payload.get("name", payload["sub"]),
            role=payload["role"],
        )
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión venció o no es válida",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _encode_token(payload: dict, secret: str) -> str:
    serializable = {
        key: int(value.timestamp()) if isinstance(value, datetime) else value
        for key, value in payload.items()
    }
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = _b64encode(json.dumps(serializable, separators=(",", ":")).encode())
    unsigned = f"{header}.{body}"
    signature = _b64encode(hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest())
    return f"{unsigned}.{signature}"


def _decode_token(token: str, secret: str) -> dict:
    header, body, signature = token.split(".")
    unsigned = f"{header}.{body}"
    expected = _b64encode(hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        raise ValueError("invalid signature")
    if json.loads(_b64decode(header)).get("alg") != "HS256":
        raise ValueError("invalid algorithm")
    payload = json.loads(_b64decode(body))
    if payload.get("iss") != "turnos-api" or not all(key in payload for key in ("sub", "exp", "role")):
        raise ValueError("invalid claims")
    if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("expired token")
    return payload
