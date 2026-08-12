from typing import Any

from supabase import Client

from app.schemas.technologies import Technology


class TechnologiesRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "technologies"

    def list_active(self, profile_id: str | None = None) -> list[Technology]:
        query = (
            self._client.table(self._table)
            .select("*")
            .eq("is_active", True)
            .order("category")
            .order("sort_order")
        )
        if profile_id:
            query = query.eq("profile_id", profile_id)

        response = query.execute()
        rows: list[dict[str, Any]] = response.data or []
        return [Technology.model_validate(row) for row in rows]
