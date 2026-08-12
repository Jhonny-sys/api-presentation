from fastapi import APIRouter, Depends, Query

from app.core.security import verify_access_token
from app.schemas.flaticon import FlaticonSearchResponse
from app.services.flaticon_service import FlaticonService

router = APIRouter(
    prefix="/flaticon",
    tags=["flaticon"],
    dependencies=[Depends(verify_access_token)],
)


@router.get("/search", response_model=FlaticonSearchResponse)
def search_flaticon_icons(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=10, le=50),
) -> FlaticonSearchResponse:
    return FlaticonService().search_icons(q, limit=limit)
