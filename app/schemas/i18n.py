import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


class I18nCreateRequest(BaseModel):
    key: str = Field(..., examples=["profile.headline"])
    source_text: str = Field(..., min_length=1)
    namespace: str | None = Field(default=None, examples=["profile"])
    description: str | None = None
    source_lang: str | None = Field(default=None, min_length=2, max_length=5)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if not KEY_PATTERN.match(value):
            raise ValueError(
                "Formato inválido. Usa namespace.slug (ej: profile.headline)"
            )
        return value


class I18nUpdateRequest(BaseModel):
    source_text: str = Field(..., min_length=1)
    description: str | None = None


class I18nTranslationPatchRequest(BaseModel):
    translated_text: str = Field(..., min_length=1)


class TranslationMeta(BaseModel):
    lang_code: str
    translated_text: str
    is_auto: bool


class I18nEntryResponse(BaseModel):
    id: UUID
    key: str
    namespace: str | None = None
    source_lang: str
    source_text: str
    description: str | None = None
    translations: dict[str, str]
    translation_meta: list[TranslationMeta]
    created_at: datetime | None = None
    updated_at: datetime | None = None


class I18nBundleResponse(BaseModel):
    lang: str
    messages: dict[str, str]


class I18nLanguagesResponse(BaseModel):
    source_lang: str
    target_languages: list[str]
    all_languages: list[str]
