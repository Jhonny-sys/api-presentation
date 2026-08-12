from collections.abc import Callable
from typing import TypeVar

import httpx
from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from app.core.supabase_errors import raise_supabase_http_error

T = TypeVar("T")


def run_supabase_query(query: Callable[[], T]) -> T:
    try:
        return query()
    except APIError as exc:
        raise_supabase_http_error(exc)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de datos temporalmente no disponible",
        ) from exc
