from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.security import verify_access_token
from app.core.supabase import get_supabase_client
from app.repositories.experience_repo import ExperienceRepository
from app.repositories.personal_info_repo import PersonalInfoRepository
from app.repositories.studies_repo import StudiesRepository
from app.repositories.technologies_repo import TechnologiesRepository
from app.schemas.experience import Experience
from app.schemas.personal_info import PersonalInfo
from app.schemas.portfolio import Portfolio
from app.schemas.portfolio_write import (
    ExperienceWrite,
    ProfileUpdate,
    StudyWrite,
    TechnologyWrite,
)
from app.schemas.studies import Study
from app.schemas.technologies import Technology
from app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["portfolio"])


def get_portfolio_service(
    client: Client = Depends(get_supabase_client),
) -> PortfolioService:
    return PortfolioService(client)


@router.get("/profile", response_model=PersonalInfo | None)
def get_profile(client: Client = Depends(get_supabase_client)) -> PersonalInfo | None:
    return PersonalInfoRepository(client).get_active()


@router.put("/profile", response_model=PersonalInfo, dependencies=[Depends(verify_access_token)])
def upsert_profile(
    body: ProfileUpdate,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PersonalInfo:
    return service.upsert_profile(body)


@router.get("/experience", response_model=list[Experience])
def list_experience(client: Client = Depends(get_supabase_client)) -> list[Experience]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return ExperienceRepository(client).list_active(profile_id)


@router.post("/experience", response_model=Experience, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_access_token)])
def create_experience(
    body: ExperienceWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Experience:
    return service.create_experience(body)


@router.put("/experience/{item_id}", response_model=Experience, dependencies=[Depends(verify_access_token)])
def update_experience(
    item_id: UUID,
    body: ExperienceWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Experience:
    try:
        return service.update_experience(item_id, body)
    except LookupError as exc:
        raise PortfolioService.not_found(exc) from exc


@router.delete("/experience/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_access_token)])
def delete_experience(
    item_id: UUID,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    service.delete_experience(item_id)


@router.get("/studies", response_model=list[Study])
def list_studies(client: Client = Depends(get_supabase_client)) -> list[Study]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return StudiesRepository(client).list_active(profile_id)


@router.post("/studies", response_model=Study, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_access_token)])
def create_study(
    body: StudyWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Study:
    return service.create_study(body)


@router.put("/studies/{item_id}", response_model=Study, dependencies=[Depends(verify_access_token)])
def update_study(
    item_id: UUID,
    body: StudyWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Study:
    try:
        return service.update_study(item_id, body)
    except LookupError as exc:
        raise PortfolioService.not_found(exc) from exc


@router.delete("/studies/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_access_token)])
def delete_study(
    item_id: UUID,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    service.delete_study(item_id)


@router.get("/technologies", response_model=list[Technology])
def list_technologies(client: Client = Depends(get_supabase_client)) -> list[Technology]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return TechnologiesRepository(client).list_active(profile_id)


@router.post("/technologies", response_model=Technology, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_access_token)])
def create_technology(
    body: TechnologyWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Technology:
    return service.create_technology(body)


@router.put("/technologies/{item_id}", response_model=Technology, dependencies=[Depends(verify_access_token)])
def update_technology(
    item_id: UUID,
    body: TechnologyWrite,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Technology:
    try:
        return service.update_technology(item_id, body)
    except LookupError as exc:
        raise PortfolioService.not_found(exc) from exc


@router.delete("/technologies/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_access_token)])
def delete_technology(
    item_id: UUID,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    service.delete_technology(item_id)


@router.get("/portfolio", response_model=Portfolio)
def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
) -> Portfolio:
    return service.get_portfolio()
