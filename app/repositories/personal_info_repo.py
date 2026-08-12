from typing import Any

from supabase import Client

from app.schemas.personal_info import PersonalInfo


class PersonalInfoRepository:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._table = "personal_info"

    def get_active(self) -> PersonalInfo | None:
        response = (
            self._client.table(self._table)
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows: list[dict[str, Any]] = response.data or []
        if not rows:
            return None
        return PersonalInfo.model_validate(rows[0])
