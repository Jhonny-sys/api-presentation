from typing import Any
from uuid import UUID

from supabase import Client

from app.repositories.base import run_supabase_query
from app.schemas.experience import Experience


class ExperienceRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "experience"

    def list_active(self, profile_id: str | None = None) -> list[Experience]:
        def query() -> list[Experience]:
            db_query = (
                self._client.table(self._table)
                .select("*")
                .eq("is_active", True)
                .order("is_current", desc=True)
                .order("start_date", desc=True)
                .order("sort_order")
            )
            if profile_id:
                db_query = db_query.eq("profile_id", profile_id)

            response = db_query.execute()
            rows: list[dict[str, Any]] = response.data or []
            return [Experience.model_validate(row) for row in rows]

        return run_supabase_query(query)

    def create(self, payload: dict[str, Any]) -> Experience:
        def query() -> Experience:
            response = self._client.table(self._table).insert(payload).execute()
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise RuntimeError("No se pudo crear la experiencia")
            return Experience.model_validate(rows[0])

        return run_supabase_query(query)

    def update(self, item_id: UUID | str, payload: dict[str, Any]) -> Experience:
        def query() -> Experience:
            response = (
                self._client.table(self._table)
                .update(payload)
                .eq("id", str(item_id))
                .eq("is_active", True)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise LookupError("Experiencia no encontrada")
            return Experience.model_validate(rows[0])

        return run_supabase_query(query)

    def soft_delete(self, item_id: UUID | str) -> None:
        def query() -> None:
            self._client.table(self._table).update({"is_active": False}).eq(
                "id", str(item_id)
            ).execute()

        run_supabase_query(query)
