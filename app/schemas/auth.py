from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    client_secret: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32)


class RevokeRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class MeResponse(BaseModel):
    subject: str
    type: str
