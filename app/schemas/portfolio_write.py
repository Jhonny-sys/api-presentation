from datetime import date

from pydantic import BaseModel, Field

from app.schemas.technologies import TechnologyCategory


class ProfileBioUpdate(BaseModel):
    bio: str = Field(..., min_length=1)


class ExperienceWrite(BaseModel):
    company: str = Field(..., min_length=1)
    description: str | None = None
    company_logo_url: str | None = None
    start_date: date
    end_date: date | None = None
    is_current: bool = False


class StudyWrite(BaseModel):
    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    certificate_url: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False


class TechnologyWrite(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    icon_url: str | None = None
    category: TechnologyCategory = "other"
