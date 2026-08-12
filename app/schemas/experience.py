from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Experience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile_id: UUID
    company: str
    role: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    location: str | None = None
    company_logo_url: str | None = None
    highlights: list[str] = Field(default_factory=list)
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
