from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    client_secret: str = Field(..., min_length=8, description="Secreto compartido con el frontend")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32, description="Refresh token opaco")


class RevokeRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32, description="Refresh token a invalidar")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Segundos hasta expiración del access token")
    refresh_expires_in: int = Field(description="Segundos hasta expiración del refresh token")
