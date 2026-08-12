from pydantic import BaseModel

from app.schemas.experience import Experience
from app.schemas.personal_info import PersonalInfo
from app.schemas.studies import Study
from app.schemas.technologies import Technology


class Portfolio(BaseModel):
    profile: PersonalInfo | None
    experience: list[Experience]
    studies: list[Study]
    technologies: list[Technology]
