from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def create_token(body: TokenRequest) -> TokenResponse:
    if body.client_secret != settings.api_client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="client_secret inválido",
        )

    return TokenResponse(
        access_token=create_access_token(),
        expires_in=settings.jwt_expire_minutes * 60,
    )
