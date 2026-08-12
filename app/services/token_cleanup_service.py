import logging
from datetime import UTC, datetime, timedelta

from supabase import Client

from app.repositories.token_cleanup_repo import TokenCleanupRepository

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL = timedelta(hours=1)


class TokenCleanupService:
    _last_run: datetime | None = None

    def __init__(self, client: Client) -> None:
        self._repo = TokenCleanupRepository(client)

    def purge_if_due(self, force: bool = False) -> dict[str, int] | None:
        now = datetime.now(UTC)

        if (
            not force
            and self._last_run is not None
            and now - self._last_run < CLEANUP_INTERVAL
        ):
            return None

        result = self._repo.purge_stale_records()
        TokenCleanupService._last_run = now
        return result

    @classmethod
    def reset_schedule(cls) -> None:
        cls._last_run = None
