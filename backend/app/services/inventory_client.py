from __future__ import annotations

import json
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from app.auth import AuthContext
from app.settings import settings


def fetch_inventory_snapshot(context: AuthContext) -> Dict[str, Any]:
    base_url = settings.inventory_service_url.rstrip("/")
    request = Request(
        f"{base_url}/api/inventory/analytics/snapshot",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {context.token}",
            "X-User-Id": context.user_id,
            "X-User-Email": context.email,
            "X-User-Name": context.name,
            "X-User-Role": context.role,
        },
        method="GET",
    )

    try:
        timeout = max(settings.inventory_service_timeout_ms / 1000, 1)
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") or str(exc)
        raise HTTPException(
            status_code=exc.code,
            detail=f"Inventory-service rechazó la extracción: {detail}",
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo obtener el snapshot de inventario desde inventory-service.",
        ) from exc
