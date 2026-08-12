from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


TechnologyCategory = Literal[
    "frontend", "backend", "database", "devops", "mobile", "tools", "other"
]


class Technology(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile_id: UUID
    name: str
    category: TechnologyCategory
    proficiency: int | None = Field(default=None, ge=1, le=5)
    icon_url: str | None = None
    years_experience: float | None = None
    is_featured: bool = False
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
