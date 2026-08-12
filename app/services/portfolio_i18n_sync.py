import logging
from uuid import UUID

from supabase import Client

from app.repositories.i18n_repo import I18nRepository
from app.schemas.experience import Experience
from app.schemas.portfolio import Portfolio
from app.schemas.studies import Study
from app.schemas.technologies import Technology
from app.services.i18n_service import I18nService

logger = logging.getLogger(__name__)


def _entity_slug(entity_id: UUID) -> str:
    # Prefijo "id_" para cumplir KEY_PATTERN (segmentos deben empezar con letra).
    return f"id_{str(entity_id).replace('-', '_')}"


def _experience_prefix(entity_id: UUID) -> str:
    return f"experience.{_entity_slug(entity_id)}"


def _study_prefix(entity_id: UUID) -> str:
    return f"studies.{_entity_slug(entity_id)}"


def _technology_prefix(entity_id: UUID) -> str:
    return f"technologies.{_entity_slug(entity_id)}"


def _sync_text(
    repo: I18nRepository,
    i18n: I18nService,
    key: str,
    text: str | None,
    namespace: str,
) -> None:
    if not text or not text.strip():
        return

    value = text.strip()
    if repo.get_entry_by_key(key):
        i18n.update_entry(key, value)
    else:
        i18n.create_entry(key, value, namespace=namespace)


def sync_experience_i18n(client: Client, item: Experience) -> None:
    repo = I18nRepository(client)
    i18n = I18nService(client)
    prefix = _experience_prefix(item.id)
    _sync_text(repo, i18n, f"{prefix}.company", item.company, "experience")
    _sync_text(repo, i18n, f"{prefix}.description", item.description, "experience")


def sync_study_i18n(client: Client, item: Study) -> None:
    repo = I18nRepository(client)
    i18n = I18nService(client)
    prefix = _study_prefix(item.id)
    _sync_text(repo, i18n, f"{prefix}.degree", item.degree, "studies")
    _sync_text(repo, i18n, f"{prefix}.institution", item.institution, "studies")


def sync_technology_i18n(client: Client, item: Technology) -> None:
    repo = I18nRepository(client)
    i18n = I18nService(client)
    prefix = _technology_prefix(item.id)
    _sync_text(repo, i18n, f"{prefix}.description", item.description, "technologies")


def ensure_experience_i18n(client: Client, item: Experience) -> None:
    repo = I18nRepository(client)
    prefix = _experience_prefix(item.id)
    desc_key = f"{prefix}.description"
    company_key = f"{prefix}.company"
    missing = (
        (item.description and not repo.get_entry_by_key(desc_key))
        or (item.company and not repo.get_entry_by_key(company_key))
    )
    if missing:
        sync_experience_i18n(client, item)


def ensure_study_i18n(client: Client, item: Study) -> None:
    repo = I18nRepository(client)
    prefix = _study_prefix(item.id)
    missing = (
        (item.degree and not repo.get_entry_by_key(f"{prefix}.degree"))
        or (item.institution and not repo.get_entry_by_key(f"{prefix}.institution"))
    )
    if missing:
        sync_study_i18n(client, item)


def ensure_technology_i18n(client: Client, item: Technology) -> None:
    repo = I18nRepository(client)
    prefix = _technology_prefix(item.id)
    desc_key = f"{prefix}.description"
    if item.description and not repo.get_entry_by_key(desc_key):
        sync_technology_i18n(client, item)


def ensure_portfolio_i18n(client: Client, portfolio: Portfolio) -> None:
    for item in portfolio.experience:
        try:
            ensure_experience_i18n(client, item)
        except Exception as exc:
            logger.warning("No se pudo sincronizar i18n de experiencia %s: %s", item.id, exc)

    for item in portfolio.studies:
        try:
            ensure_study_i18n(client, item)
        except Exception as exc:
            logger.warning("No se pudo sincronizar i18n de estudio %s: %s", item.id, exc)

    for item in portfolio.technologies:
        try:
            ensure_technology_i18n(client, item)
        except Exception as exc:
            logger.warning("No se pudo sincronizar i18n de tecnología %s: %s", item.id, exc)
