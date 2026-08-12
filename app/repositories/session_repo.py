from typing import Any
from uuid import UUID

from supabase import Client

from app.repositories.base import run_supabase_query


class SessionRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "revoked_sessions"

    def revoke_family(self, family_id: UUID) -> None:
        def query() -> None:
            self._client.table(self._table).upsert(
                {"family_id": str(family_id)},
                on_conflict="family_id",
            ).execute()

        run_supabase_query(query)

    def is_family_revoked(self, family_id: UUID) -> bool:
        def query() -> bool:
            response = (
                self._client.table(self._table)
                .select("family_id")
                .eq("family_id", str(family_id))
                .limit(1)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            return len(rows) > 0

        return run_supabase_query(query)
