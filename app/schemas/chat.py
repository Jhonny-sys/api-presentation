from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    lang: Literal["es", "en", "pt"] = "es"
    turn: int = Field(..., ge=1, le=3)


class ChatResponse(BaseModel):
    reply: str
    turn: int
    turns_remaining: int
    suggest_contact: bool
