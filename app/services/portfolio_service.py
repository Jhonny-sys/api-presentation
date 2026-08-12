from uuid import UUID

import logging

from fastapi import HTTPException, status
from supabase import Client

from app.repositories.experience_repo import ExperienceRepository
from app.repositories.i18n_repo import I18nRepository
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
from app.services.i18n_service import I18nService

DEFAULT_FULL_NAME = "Jhonny Alexander Fonseca"
DEFAULT_HEADLINE = "Desarrollador"
PROFILE_BIO_I18N_KEY = "profile.bio"

logger = logging.getLogger(__name__)


class PortfolioService:
    def __init__(self, client: Client) -> None:
        self._client = client
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

    def _profile_id(self) -> str:
        profile = self._personal_info.get_active()
        if profile:
            return str(profile.id)

        created = self._personal_info.create(
            {
                "full_name": DEFAULT_FULL_NAME,
                "headline": DEFAULT_HEADLINE,
                "bio": "",
                "is_active": True,
            }
        )
        return str(created.id)

    def upsert_profile(self, body: ProfileUpdate) -> PersonalInfo:
        payload = body.model_dump(exclude_unset=True)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No hay datos para actualizar",
            )

        profile = self._personal_info.get_active()
        if profile:
            result = self._personal_info.update(str(profile.id), payload)
        else:
            result = self._personal_info.create(
                {
                    "full_name": DEFAULT_FULL_NAME,
                    "headline": DEFAULT_HEADLINE,
                    "bio": payload.get("bio", ""),
                    "avatar_url": payload.get("avatar_url"),
                    "resume_url": payload.get("resume_url"),
                    "letter_url": payload.get("letter_url"),
                    "is_active": True,
                }
            )

        if "bio" in payload and payload["bio"] is not None:
            self._sync_profile_bio_i18n(payload["bio"])
        return result

    def _sync_profile_bio_i18n(self, bio: str) -> None:
        if not bio.strip():
            return

        try:
            repo = I18nRepository(self._client)
            i18n = I18nService(self._client)
            if repo.get_entry_by_key(PROFILE_BIO_I18N_KEY):
                i18n.update_entry(PROFILE_BIO_I18N_KEY, bio)
            else:
                i18n.create_entry(PROFILE_BIO_I18N_KEY, bio, namespace="profile")
        except Exception as exc:
            logger.warning("No se pudo sincronizar profile.bio con i18n: %s", exc)

    def create_experience(self, body: ExperienceWrite) -> Experience:
        end_date = None if body.is_current else body.end_date
        return self._experience.create(
            {
                "profile_id": self._profile_id(),
                "company": body.company.strip(),
                "role": body.company.strip(),
                "description": body.description,
                "company_logo_url": body.company_logo_url,
                "start_date": body.start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "is_current": body.is_current,
                "is_active": True,
            }
        )

    def update_experience(self, item_id: UUID, body: ExperienceWrite) -> Experience:
        end_date = None if body.is_current else body.end_date
        return self._experience.update(
            item_id,
            {
                "company": body.company.strip(),
                "role": body.company.strip(),
                "description": body.description,
                "company_logo_url": body.company_logo_url,
                "start_date": body.start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "is_current": body.is_current,
            },
        )

    def delete_experience(self, item_id: UUID) -> None:
        self._experience.soft_delete(item_id)

    def create_study(self, body: StudyWrite) -> Study:
        end_date = None if body.is_current else body.end_date
        return self._studies.create(
            {
                "profile_id": self._profile_id(),
                "institution": body.institution.strip(),
                "degree": body.degree.strip(),
                "certificate_url": body.certificate_url,
                "start_date": body.start_date.isoformat() if body.start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "is_current": body.is_current,
                "is_active": True,
            }
        )

    def update_study(self, item_id: UUID, body: StudyWrite) -> Study:
        end_date = None if body.is_current else body.end_date
        return self._studies.update(
            item_id,
            {
                "institution": body.institution.strip(),
                "degree": body.degree.strip(),
                "certificate_url": body.certificate_url,
                "start_date": body.start_date.isoformat() if body.start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "is_current": body.is_current,
            },
        )

    def delete_study(self, item_id: UUID) -> None:
        self._studies.soft_delete(item_id)

    def create_technology(self, body: TechnologyWrite) -> Technology:
        return self._technologies.create(
            {
                "profile_id": self._profile_id(),
                "name": body.name.strip(),
                "description": body.description,
                "icon_url": body.icon_url,
                "category": body.category,
                "is_active": True,
            }
        )

    def update_technology(self, item_id: UUID, body: TechnologyWrite) -> Technology:
        return self._technologies.update(
            item_id,
            {
                "name": body.name.strip(),
                "description": body.description,
                "icon_url": body.icon_url,
                "category": body.category,
            },
        )

    def delete_technology(self, item_id: UUID) -> None:
        self._technologies.soft_delete(item_id)

    @staticmethod
    def not_found(exc: Exception) -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
