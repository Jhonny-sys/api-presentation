from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    client_secret: str = Field(..., min_length=8, description="Secreto compartido con el frontend")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
