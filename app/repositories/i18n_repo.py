from typing import Any
from uuid import UUID

from supabase import Client

from app.repositories.base import run_supabase_query


class I18nRepository:
    def __init__(self, client: Client) -> None:
        self._entries = "i18n_entries"
        self._translations = "i18n_translations"
        self._client = client

    def create_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        def query() -> dict[str, Any]:
            response = self._client.table(self._entries).insert(payload).execute()
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise RuntimeError("No se pudo crear la entrada i18n")
            return rows[0]

        return run_supabase_query(query)

    def update_entry(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        def query() -> dict[str, Any]:
            response = (
                self._client.table(self._entries)
                .update(payload)
                .eq("key", key)
                .eq("is_active", True)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise LookupError(f"Clave i18n no encontrada: {key}")
            return rows[0]

        return run_supabase_query(query)

    def get_entry_by_key(self, key: str) -> dict[str, Any] | None:
        def query() -> dict[str, Any] | None:
            response = (
                self._client.table(self._entries)
                .select("*")
                .eq("key", key)
                .eq("is_active", True)
                .limit(1)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            return rows[0] if rows else None

        return run_supabase_query(query)

    def list_entries(self, namespace: str | None = None) -> list[dict[str, Any]]:
        def query() -> list[dict[str, Any]]:
            db_query = (
                self._client.table(self._entries)
                .select("*")
                .eq("is_active", True)
                .order("namespace")
                .order("key")
            )
            if namespace:
                db_query = db_query.eq("namespace", namespace)

            response = db_query.execute()
            return response.data or []

        return run_supabase_query(query)

    def upsert_translation(
        self,
        entry_id: UUID | str,
        lang_code: str,
        translated_text: str,
        is_auto: bool,
    ) -> dict[str, Any]:
        def query() -> dict[str, Any]:
            payload = {
                "entry_id": str(entry_id),
                "lang_code": lang_code,
                "translated_text": translated_text,
                "is_auto": is_auto,
            }
            response = (
                self._client.table(self._translations)
                .upsert(payload, on_conflict="entry_id,lang_code")
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise RuntimeError("No se pudo guardar la traducción")
            return rows[0]

        return run_supabase_query(query)

    def get_translations_for_entry(self, entry_id: UUID | str) -> list[dict[str, Any]]:
        def query() -> list[dict[str, Any]]:
            response = (
                self._client.table(self._translations)
                .select("*")
                .eq("entry_id", str(entry_id))
                .order("lang_code")
                .execute()
            )
            return response.data or []

        return run_supabase_query(query)

    def get_translation(self, entry_id: UUID | str, lang_code: str) -> dict[str, Any] | None:
        def query() -> dict[str, Any] | None:
            response = (
                self._client.table(self._translations)
                .select("*")
                .eq("entry_id", str(entry_id))
                .eq("lang_code", lang_code)
                .limit(1)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            return rows[0] if rows else None

        return run_supabase_query(query)

    def get_bundle(self, lang_code: str) -> dict[str, str]:
        def query() -> dict[str, str]:
            entries_response = (
                self._client.table(self._entries)
                .select("id, key, source_lang, source_text")
                .eq("is_active", True)
                .execute()
            )
            entries: list[dict[str, Any]] = entries_response.data or []
            if not entries:
                return {}

            entry_ids = [entry["id"] for entry in entries]
            translations_response = (
                self._client.table(self._translations)
                .select("entry_id, lang_code, translated_text")
                .in_("entry_id", entry_ids)
                .eq("lang_code", lang_code)
                .execute()
            )
            translations: list[dict[str, Any]] = translations_response.data or []
            by_entry = {row["entry_id"]: row["translated_text"] for row in translations}

            bundle: dict[str, str] = {}
            for entry in entries:
                key = entry["key"]
                if entry["source_lang"] == lang_code:
                    bundle[key] = entry["source_text"]
                elif entry["id"] in by_entry:
                    bundle[key] = by_entry[entry["id"]]
            return bundle

        return run_supabase_query(query)
