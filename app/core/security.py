import logging
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from supabase import Client

from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.repositories.session_repo import SessionRepository

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

ACCESS_TOKEN_TYPE = "access"
FAMILY_ID_CLAIM = "fid"


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def hash_refresh_token(token: str) -> str:
    material = f"{token}{settings.refresh_token_pepper}".encode()
    return hashlib.sha256(material).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def create_access_token(family_id: UUID, subject: str = "portfolio-client") -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": subject,
        "type": ACCESS_TOKEN_TYPE,
        FAMILY_ID_CLAIM: str(family_id),
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _decode_access_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT requerido. Envía: Authorization: Bearer <access_token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_bearer_token(credentials.credentials)


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )

    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidTokenError("invalid token type")

    if not payload.get(FAMILY_ID_CLAIM):
        raise InvalidTokenError("missing family id")

    return payload


def verify_bearer_token(token: str) -> dict:
    try:
        return decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def verify_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    client: Client = Depends(get_supabase_client),
) -> dict:
    payload = _decode_access_token(credentials)
    family_id = UUID(payload[FAMILY_ID_CLAIM])

    try:
        revoked = SessionRepository(client).is_family_revoked(family_id)
    except httpx.HTTPError as exc:
        logger.error("Supabase no disponible al validar sesión: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de datos temporalmente no disponible",
        ) from exc

    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión revocada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


class AuthTokenService:
    def __init__(self, client: Client) -> None:
        self._refresh_repo = RefreshTokenRepository(client)
        self._session_repo = SessionRepository(client)

    def issue_token_pair(self, subject: str = "portfolio-client") -> dict[str, str | int]:
        family_id = uuid4()
        refresh_token = generate_refresh_token()
        token_hash = hash_refresh_token(refresh_token)
        expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days)

        self._refresh_repo.create(
            family_id=family_id,
            token_hash=token_hash,
            subject=subject,
            expires_at=expires_at,
        )

        return self._build_response(subject, refresh_token, family_id)

    def refresh_tokens(self, refresh_token: str) -> dict[str, str | int]:
        token_hash = hash_refresh_token(refresh_token)
        stored = self._refresh_repo.get_by_hash(token_hash)

        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
            )

        family_id = UUID(stored["family_id"])

        if stored["revoked_at"] is not None:
            self._revoke_session(family_id)
            logger.warning(
                "Reutilización de refresh token detectada. Familia revocada: %s",
                family_id,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token reutilizado. Sesión invalidada por seguridad.",
            )

        expires_at = _parse_datetime(stored["expires_at"])
        if expires_at <= datetime.now(UTC):
            self._refresh_repo.revoke_by_id(UUID(stored["id"]))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado",
            )

        new_refresh_token = generate_refresh_token()
        new_hash = hash_refresh_token(new_refresh_token)
        new_expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days)

        new_record = self._refresh_repo.create(
            family_id=family_id,
            token_hash=new_hash,
            subject=stored["subject"],
            expires_at=new_expires_at,
        )
        self._refresh_repo.revoke_by_id(UUID(stored["id"]), replaced_by=UUID(new_record["id"]))

        return self._build_response(stored["subject"], new_refresh_token, family_id)

    def revoke_refresh_token(self, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        stored = self._refresh_repo.get_by_hash(token_hash)
        if stored is None:
            return
        self._revoke_session(UUID(stored["family_id"]))

    def _revoke_session(self, family_id: UUID) -> None:
        self._refresh_repo.revoke_family(family_id)
        self._session_repo.revoke_family(family_id)

    def _build_response(
        self,
        subject: str,
        refresh_token: str,
        family_id: UUID,
    ) -> dict[str, str | int]:
        return {
            "access_token": create_access_token(family_id, subject),
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_minutes * 60,
            "refresh_expires_in": settings.jwt_refresh_expire_days * 86400,
        }
