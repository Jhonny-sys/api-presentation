from supabase import Client

from app.repositories.experience_repo import ExperienceRepository
from app.repositories.personal_info_repo import PersonalInfoRepository
from app.repositories.studies_repo import StudiesRepository
from app.repositories.technologies_repo import TechnologiesRepository
from app.schemas.portfolio import Portfolio


class PortfolioService:
    def __init__(self, client: Client) -> None:
        self._personal_info = PersonalInfoRepository(client)
        self._experience = ExperienceRepository(client)
        self._studies = StudiesRepository(client)
        self._technologies = TechnologiesRepository(client)

    def get_portfolio(self) -> Portfolio:
        profile = self._personal_info.get_active()
        profile_id = str(profile.id) if profile else None

        return Portfolio(
            profile=profile,
            experience=self._experience.list_active(profile_id),
            studies=self._studies.list_active(profile_id),
            technologies=self._technologies.list_active(profile_id),
        )
