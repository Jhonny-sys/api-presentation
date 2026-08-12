from fastapi import APIRouter, Depends
from supabase import Client

from app.core.supabase import get_supabase_client
from app.repositories.experience_repo import ExperienceRepository
from app.repositories.personal_info_repo import PersonalInfoRepository
from app.repositories.studies_repo import StudiesRepository
from app.repositories.technologies_repo import TechnologiesRepository
from app.schemas.experience import Experience
from app.schemas.personal_info import PersonalInfo
from app.schemas.portfolio import Portfolio
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


@router.get("/experience", response_model=list[Experience])
def list_experience(client: Client = Depends(get_supabase_client)) -> list[Experience]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return ExperienceRepository(client).list_active(profile_id)


@router.get("/studies", response_model=list[Study])
def list_studies(client: Client = Depends(get_supabase_client)) -> list[Study]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return StudiesRepository(client).list_active(profile_id)


@router.get("/technologies", response_model=list[Technology])
def list_technologies(client: Client = Depends(get_supabase_client)) -> list[Technology]:
    profile = PersonalInfoRepository(client).get_active()
    profile_id = str(profile.id) if profile else None
    return TechnologiesRepository(client).list_active(profile_id)


@router.get("/portfolio", response_model=Portfolio)
def get_portfolio(
    service: PortfolioService = Depends(get_portfolio_service),
) -> Portfolio:
    return service.get_portfolio()
