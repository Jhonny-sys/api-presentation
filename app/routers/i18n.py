from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.core.security import verify_access_token
from app.core.supabase import get_supabase_client
from app.core.config import settings
from app.schemas.i18n import (
    I18nBundleResponse,
    I18nCreateRequest,
    I18nEntryResponse,
    I18nLanguagesResponse,
    I18nTranslationPatchRequest,
    I18nUpdateRequest,
)
from app.services.i18n_service import I18nService

router = APIRouter(
    prefix="/i18n",
    tags=["i18n"],
)


def get_i18n_service(client: Client = Depends(get_supabase_client)) -> I18nService:
    return I18nService(client)


@router.get("/languages", response_model=I18nLanguagesResponse)
def list_supported_languages() -> I18nLanguagesResponse:
    return I18nLanguagesResponse(
        source_lang=settings.i18n_source_lang,
        target_languages=settings.i18n_target_languages_list,
        all_languages=settings.i18n_all_languages_list,
    )


@router.post("", response_model=I18nEntryResponse, status_code=201, dependencies=[Depends(verify_access_token)])
def create_i18n_entry(
    body: I18nCreateRequest,
    service: I18nService = Depends(get_i18n_service),
) -> I18nEntryResponse:
    result = service.create_entry(
        key=body.key,
        source_text=body.source_text,
        namespace=body.namespace,
        description=body.description,
        source_lang=body.source_lang,
    )
    return I18nEntryResponse(**result)


@router.get("", response_model=list[I18nEntryResponse], dependencies=[Depends(verify_access_token)])
def list_i18n_entries(
    namespace: str | None = Query(default=None),
    service: I18nService = Depends(get_i18n_service),
) -> list[I18nEntryResponse]:
    results = service.list_entries(namespace=namespace)
    return [I18nEntryResponse(**item) for item in results]


@router.get("/bundle/{lang_code}", response_model=I18nBundleResponse)
def get_i18n_bundle(
    lang_code: str,
    service: I18nService = Depends(get_i18n_service),
) -> I18nBundleResponse:
    result = service.get_bundle(lang_code.lower())
    return I18nBundleResponse(**result)


@router.get("/{key:path}", response_model=I18nEntryResponse, dependencies=[Depends(verify_access_token)])
def get_i18n_entry(
    key: str,
    service: I18nService = Depends(get_i18n_service),
) -> I18nEntryResponse:
    result = service.get_entry(key)
    return I18nEntryResponse(**result)


@router.put("/{key:path}", response_model=I18nEntryResponse, dependencies=[Depends(verify_access_token)])
def update_i18n_entry(
    key: str,
    body: I18nUpdateRequest,
    service: I18nService = Depends(get_i18n_service),
) -> I18nEntryResponse:
    result = service.update_entry(
        key=key,
        source_text=body.source_text,
        description=body.description,
    )
    return I18nEntryResponse(**result)


@router.patch("/{key:path}/translations/{lang_code}", response_model=I18nEntryResponse, dependencies=[Depends(verify_access_token)])
def patch_i18n_translation(
    key: str,
    lang_code: str,
    body: I18nTranslationPatchRequest,
    service: I18nService = Depends(get_i18n_service),
) -> I18nEntryResponse:
    result = service.update_translation_manual(
        key=key,
        lang_code=lang_code.lower(),
        translated_text=body.translated_text,
    )
    return I18nEntryResponse(**result)
