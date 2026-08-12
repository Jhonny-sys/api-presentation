import logging
from uuid import UUID

import httpx
from jwt.exceptions import InvalidTokenError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.supabase import get_supabase_client
from app.repositories.session_repo import SessionRepository

logger = logging.getLogger(__name__)

PUBLIC_API_PATHS = frozenset(
    {
        f"{settings.api_prefix}/auth/login",
        f"{settings.api_prefix}/auth/token",
        f"{settings.api_prefix}/auth/refresh",
        f"{settings.api_prefix}/auth/revoke",
    }
)

PUBLIC_GET_PATHS = frozenset(
    {
        f"{settings.api_prefix}/portfolio",
        f"{settings.api_prefix}/profile",
        f"{settings.api_prefix}/experience",
        f"{settings.api_prefix}/studies",
        f"{settings.api_prefix}/technologies",
        f"{settings.api_prefix}/i18n/languages",
    }
)

PUBLIC_GET_PREFIXES = (
    f"{settings.api_prefix}/i18n/bundle/",
)

PUBLIC_POST_PATHS = frozenset(
    {
        f"{settings.api_prefix}/chat",
    }
)


def is_public_api_request(method: str, path: str) -> bool:
    if path in PUBLIC_API_PATHS:
        return True
    if method == "POST" and path in PUBLIC_POST_PATHS:
        return True
    if method != "GET":
        return False
    if path in PUBLIC_GET_PATHS:
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_GET_PREFIXES)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        if path == "/health" or not path.startswith(settings.api_prefix):
            return await call_next(request)

        if is_public_api_request(request.method, path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Token JWT requerido. Envía: Authorization: Bearer <access_token>"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
        except InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token inválido o expirado"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        family_id = UUID(payload["fid"])
        try:
            revoked = SessionRepository(get_supabase_client()).is_family_revoked(family_id)
        except httpx.HTTPError as exc:
            logger.error("Supabase no disponible al validar sesión: %s", exc)
            return JSONResponse(
                status_code=503,
                content={"detail": "Servicio de datos temporalmente no disponible"},
            )

        if revoked:
            return JSONResponse(
                status_code=401,
                content={"detail": "Sesión revocada"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.auth = payload
        return await call_next(request)
