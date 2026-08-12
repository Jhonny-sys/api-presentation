from typing import Any

from supabase import Client

from app.schemas.studies import Study


class StudiesRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "studies"

    def list_active(self, profile_id: str | None = None) -> list[Study]:
        query = (
            self._client.table(self._table)
            .select("*")
            .eq("is_active", True)
            .order("is_current", desc=True)
            .order("end_date", desc=True)
            .order("sort_order")
        )
        if profile_id:
            query = query.eq("profile_id", profile_id)

        response = query.execute()
        rows: list[dict[str, Any]] = response.data or []
        return [Study.model_validate(row) for row in rows]
