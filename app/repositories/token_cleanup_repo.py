import logging
from datetime import UTC, datetime, timedelta

from supabase import Client

from app.core.config import settings
from app.repositories.base import run_supabase_query

logger = logging.getLogger(__name__)


class TokenCleanupRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def purge_stale_records(self) -> dict[str, int]:
        now = datetime.now(UTC)
        revoked_session_cutoff = now - timedelta(minutes=settings.jwt_expire_minutes + 5)

        refresh_deleted = self._purge_refresh_tokens(now)
        sessions_deleted = self._purge_revoked_sessions(revoked_session_cutoff)

        if refresh_deleted or sessions_deleted:
            logger.info(
                "Limpieza de tokens: refresh_tokens=%s, revoked_sessions=%s",
                refresh_deleted,
                sessions_deleted,
            )

        return {
            "refresh_tokens_deleted": refresh_deleted,
            "revoked_sessions_deleted": sessions_deleted,
        }

    def _purge_refresh_tokens(self, now: datetime) -> int:
        def query() -> int:
            response = (
                self._client.table("refresh_tokens")
                .delete()
                .lt("expires_at", now.isoformat())
                .execute()
            )
            rows = response.data or []
            return len(rows)

        return run_supabase_query(query)

    def _purge_revoked_sessions(self, cutoff: datetime) -> int:
        def query() -> int:
            response = (
                self._client.table("revoked_sessions")
                .delete()
                .lt("revoked_at", cutoff.isoformat())
                .execute()
            )
            rows = response.data or []
            return len(rows)

        return run_supabase_query(query)
