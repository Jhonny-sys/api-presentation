import re
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.config import settings
from app.repositories.i18n_repo import I18nRepository
from app.services.translation_service import translate_to_all_languages

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


class I18nService:
    def __init__(self, client: Client) -> None:
        self._repo = I18nRepository(client)

    def create_entry(
        self,
        key: str,
        source_text: str,
        namespace: str | None = None,
        description: str | None = None,
        source_lang: str | None = None,
    ) -> dict[str, Any]:
        self._validate_key(key)

        if self._repo.get_entry_by_key(key):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La clave '{key}' ya existe",
            )

        source = source_lang or settings.i18n_source_lang
        derived_namespace = namespace or key.split(".")[0]

        entry = self._repo.create_entry(
            {
                "key": key,
                "namespace": derived_namespace,
                "source_lang": source,
                "source_text": source_text,
                "description": description,
            }
        )

        translations_map = translate_to_all_languages(source_text, source)
        self._save_translations(entry["id"], translations_map, is_auto=True)

        return self._build_detail(entry, translations_map)

    def update_entry(
        self,
        key: str,
        source_text: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        entry = self._repo.get_entry_by_key(key)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clave i18n no encontrada: {key}",
            )

        payload: dict[str, Any] = {"source_text": source_text}
        if description is not None:
            payload["description"] = description

        updated = self._repo.update_entry(key, payload)
        translations_map = translate_to_all_languages(source_text, updated["source_lang"])
        self._save_translations(updated["id"], translations_map, is_auto=True)

        return self._build_detail(updated, translations_map)

    def get_entry(self, key: str) -> dict[str, Any]:
        entry = self._repo.get_entry_by_key(key)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clave i18n no encontrada: {key}",
            )

        translations = self._repo.get_translations_for_entry(entry["id"])
        translations_map = {row["lang_code"]: row["translated_text"] for row in translations}
        if entry["source_lang"] not in translations_map:
            translations_map[entry["source_lang"]] = entry["source_text"]

        return self._build_detail(entry, translations_map, translations)

    def list_entries(self, namespace: str | None = None) -> list[dict[str, Any]]:
        entries = self._repo.list_entries(namespace)
        results: list[dict[str, Any]] = []

        for entry in entries:
            translations = self._repo.get_translations_for_entry(entry["id"])
            translations_map = {row["lang_code"]: row["translated_text"] for row in translations}
            if entry["source_lang"] not in translations_map:
                translations_map[entry["source_lang"]] = entry["source_text"]
            results.append(self._build_detail(entry, translations_map, translations))

        return results

    def get_bundle(self, lang_code: str) -> dict[str, Any]:
        if lang_code not in settings.i18n_all_languages_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Idioma no soportado: {lang_code}",
            )

        messages = self._repo.get_bundle(lang_code)
        return {"lang": lang_code, "messages": messages}

    def update_translation_manual(
        self,
        key: str,
        lang_code: str,
        translated_text: str,
    ) -> dict[str, Any]:
        entry = self._repo.get_entry_by_key(key)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clave i18n no encontrada: {key}",
            )

        if lang_code not in settings.i18n_all_languages_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Idioma no soportado: {lang_code}",
            )

        self._repo.upsert_translation(
            entry_id=entry["id"],
            lang_code=lang_code,
            translated_text=translated_text,
            is_auto=False,
        )

        return self.get_entry(key)

    def _save_translations(
        self,
        entry_id: UUID | str,
        translations_map: dict[str, str],
        is_auto: bool,
    ) -> None:
        for lang_code, translated_text in translations_map.items():
            self._repo.upsert_translation(
                entry_id=entry_id,
                lang_code=lang_code,
                translated_text=translated_text,
                is_auto=is_auto,
            )

    def _build_detail(
        self,
        entry: dict[str, Any],
        translations_map: dict[str, str],
        translation_rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if translation_rows is None:
            translation_rows = [
                {
                    "lang_code": lang,
                    "translated_text": text,
                    "is_auto": lang != entry["source_lang"],
                }
                for lang, text in translations_map.items()
            ]
        else:
            translation_rows = [
                {
                    "lang_code": row["lang_code"],
                    "translated_text": row["translated_text"],
                    "is_auto": row["is_auto"],
                }
                for row in translation_rows
            ]

        return {
            "id": entry["id"],
            "key": entry["key"],
            "namespace": entry.get("namespace"),
            "source_lang": entry["source_lang"],
            "source_text": entry["source_text"],
            "description": entry.get("description"),
            "translations": translations_map,
            "translation_meta": translation_rows,
            "created_at": entry.get("created_at"),
            "updated_at": entry.get("updated_at"),
        }

    @staticmethod
    def _validate_key(key: str) -> None:
        if not KEY_PATTERN.match(key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Formato de key inválido. Usa namespace.slug "
                    "(ej: profile.headline, experience.company_1.role)"
                ),
            )
