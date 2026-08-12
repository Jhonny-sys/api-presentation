import logging
import time

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.flaticon import FlaticonIconItem, FlaticonSearchResponse

logger = logging.getLogger(__name__)

BASE_URL = "https://api.flaticon.com/v3"
_token_cache: dict[str, float | str] = {"token": "", "expires_at": 0.0}


class FlaticonService:
    def __init__(self) -> None:
        if not settings.flaticon_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Flaticon no configurado. Agrega FLATICON_API_KEY en el backend "
                    "(gratis en https://api.flaticon.com)."
                ),
            )

    def search_icons(self, query: str, limit: int = 20) -> FlaticonSearchResponse:
        term = query.strip()
        if not term:
            return FlaticonSearchResponse(items=[], query=term)

        token = self._get_token()
        params = {"q": term, "limit": min(max(limit, 10), 50)}
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                f"{BASE_URL}/search/icons/priority",
                params=params,
                headers=headers,
            )

        if response.status_code == 401:
            _token_cache["expires_at"] = 0.0
            token = self._get_token(force=True)
            headers["Authorization"] = f"Bearer {token}"
            with httpx.Client(timeout=20.0) as client:
                response = client.get(
                    f"{BASE_URL}/search/icons/priority",
                    params=params,
                    headers=headers,
                )

        if response.status_code != 200:
            logger.warning("Flaticon search failed: %s %s", response.status_code, response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo buscar iconos en Flaticon",
            )

        payload = response.json()
        raw_items = payload.get("data") or payload.get("items") or []
        items: list[FlaticonIconItem] = []

        for item in raw_items:
            images = item.get("images") or {}
            icon_url = images.get("512") or images.get("256") or images.get("128")
            preview_url = images.get("128") or images.get("64") or icon_url
            if not icon_url:
                continue

            items.append(
                FlaticonIconItem(
                    id=int(item.get("id") or 0),
                    description=str(item.get("description") or item.get("name") or "Icono"),
                    preview_url=preview_url,
                    icon_url=icon_url,
                )
            )

        return FlaticonSearchResponse(items=items, query=term)

    def _get_token(self, force: bool = False) -> str:
        now = time.time()
        cached = str(_token_cache.get("token") or "")
        expires_at = float(_token_cache.get("expires_at") or 0)
        if cached and not force and now < expires_at - 300:
            return cached

        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{BASE_URL}/app/authentication",
                data={"apikey": settings.flaticon_api_key},
            )

        if response.status_code != 200:
            logger.warning("Flaticon auth failed: %s", response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo autenticar con Flaticon",
            )

        data = response.json()
        token = str(data.get("token") or "")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Respuesta inválida de Flaticon",
            )

        expires = float(data.get("expires") or (now + 86400))
        _token_cache["token"] = token
        _token_cache["expires_at"] = expires
        return token
