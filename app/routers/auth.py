from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.config import settings
from app.core.security import AuthTokenService
from app.core.supabase import get_supabase_client
from app.schemas.auth import RefreshRequest, RevokeRequest, TokenRequest, TokenResponse
from app.services.token_cleanup_service import TokenCleanupService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(client: Client = Depends(get_supabase_client)) -> AuthTokenService:
    return AuthTokenService(client)


def get_cleanup_service(client: Client = Depends(get_supabase_client)) -> TokenCleanupService:
    return TokenCleanupService(client)


@router.post("/token", response_model=TokenResponse)
def create_token(
    body: TokenRequest,
    service: AuthTokenService = Depends(get_auth_service),
    cleanup: TokenCleanupService = Depends(get_cleanup_service),
) -> TokenResponse:
    if body.client_secret != settings.api_client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="client_secret inválido",
        )

    tokens = service.issue_token_pair()
    cleanup.purge_if_due()
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    body: RefreshRequest,
    service: AuthTokenService = Depends(get_auth_service),
    cleanup: TokenCleanupService = Depends(get_cleanup_service),
) -> TokenResponse:
    tokens = service.refresh_tokens(body.refresh_token)
    cleanup.purge_if_due()
    return TokenResponse(**tokens)


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_token(
    body: RevokeRequest,
    service: AuthTokenService = Depends(get_auth_service),
    cleanup: TokenCleanupService = Depends(get_cleanup_service),
) -> None:
    service.revoke_refresh_token(body.refresh_token)
    cleanup.purge_if_due(force=True)
