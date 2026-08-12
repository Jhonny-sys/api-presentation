from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Study(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile_id: UUID
    institution: str
    degree: str
    field_of_study: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    certificate_url: str | None = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
