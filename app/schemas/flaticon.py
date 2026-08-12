from pydantic import BaseModel, Field


class FlaticonIconItem(BaseModel):
    id: int
    description: str
    preview_url: str
    icon_url: str
    attribution: str = "Icono por Flaticon"


class FlaticonSearchResponse(BaseModel):
    items: list[FlaticonIconItem] = Field(default_factory=list)
    query: str
