from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Callable, Iterable

from fastapi import Header, HTTPException, status

from app.settings import settings


@dataclass(frozen=True)
class AuthContext:
    token: str
    user_id: str
    email: str
    name: str
    role: str


def _decode_part(value: str) -> dict:
    padding = "=" * (-len(value) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(f"{value}{padding}").decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT inválido.") from exc


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT requerido.")
    return authorization[7:].strip()


def _verify_hs256(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT inválido.")

    header = _decode_part(parts[0])
    payload = _decode_part(parts[1])
    if header.get("alg") != "HS256":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Algoritmo JWT no soportado.")

    expected = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        f"{parts[0]}.{parts[1]}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_signature = base64.urlsafe_b64encode(expected).rstrip(b"=").decode("utf-8")
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firma JWT inválida.")

    exp = payload.get("exp")
    if exp is not None and int(exp) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token JWT expirado.")

    return payload


def get_auth_context(authorization: str | None = Header(default=None)) -> AuthContext:
    token = _extract_token(authorization)
    payload = _verify_hs256(token)
    role = str(payload.get("rol") or payload.get("role") or "").upper().replace("ROLE_", "")
    return AuthContext(
        token=token,
        user_id=str(payload.get("userId") or payload.get("user_id") or ""),
        email=str(payload.get("sub") or payload.get("email") or ""),
        name=str(payload.get("name") or ""),
        role=role,
    )


def require_roles(*allowed_roles: str) -> Callable[[str | None], AuthContext]:
    allowed = {role.upper().replace("ROLE_", "") for role in allowed_roles}

    def dependency(authorization: str | None = Header(default=None)) -> AuthContext:
        context = get_auth_context(authorization)
        if context.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ejecutar esta operación.",
            )
        return context

    return dependency


def ensure_dev_seed_enabled(context: AuthContext, allowed_roles: Iterable[str]) -> None:
    allowed = {role.upper() for role in allowed_roles}
    if context.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operación no autorizada.")
    if not settings.enable_dev_seed_endpoints:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La generación de datos de prueba está deshabilitada en este ambiente.",
        )
