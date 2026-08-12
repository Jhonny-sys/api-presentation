from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from supabase import Client

from app.repositories.base import run_supabase_query


class RefreshTokenRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "refresh_tokens"

    def create(
        self,
        family_id: UUID,
        token_hash: str,
        subject: str,
        expires_at: datetime,
    ) -> dict[str, Any]:
        def query() -> dict[str, Any]:
            response = (
                self._client.table(self._table)
                .insert(
                    {
                        "family_id": str(family_id),
                        "token_hash": token_hash,
                        "subject": subject,
                        "expires_at": expires_at.isoformat(),
                    }
                )
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            if not rows:
                raise RuntimeError("No se pudo crear el refresh token")
            return rows[0]

        return run_supabase_query(query)

    def get_by_hash(self, token_hash: str) -> dict[str, Any] | None:
        def query() -> dict[str, Any] | None:
            response = (
                self._client.table(self._table)
                .select("*")
                .eq("token_hash", token_hash)
                .limit(1)
                .execute()
            )
            rows: list[dict[str, Any]] = response.data or []
            return rows[0] if rows else None

        return run_supabase_query(query)

    def revoke_by_id(self, token_id: UUID, replaced_by: UUID | None = None) -> None:
        def query() -> None:
            payload: dict[str, Any] = {"revoked_at": datetime.now(UTC).isoformat()}
            if replaced_by:
                payload["replaced_by"] = str(replaced_by)
            self._client.table(self._table).update(payload).eq("id", str(token_id)).execute()

        run_supabase_query(query)

    def revoke_family(self, family_id: UUID) -> None:
        def query() -> None:
            self._client.table(self._table).update(
                {"revoked_at": datetime.now(UTC).isoformat()}
            ).eq("family_id", str(family_id)).is_("revoked_at", "null").execute()

        run_supabase_query(query)
