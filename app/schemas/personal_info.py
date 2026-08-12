from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SocialLinks


class PersonalInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    headline: str
    bio: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    avatar_url: str | None = None
    resume_url: str | None = None
    letter_url: str | None = None
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    available_for_work: bool = True
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
