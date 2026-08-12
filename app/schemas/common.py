from pydantic import BaseModel


class SocialLinks(BaseModel):
    github: str | None = None
    linkedin: str | None = None
    website: str | None = None
