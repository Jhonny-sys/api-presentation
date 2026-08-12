from collections.abc import Callable
from typing import TypeVar

from postgrest.exceptions import APIError

from app.core.supabase_errors import raise_supabase_http_error

T = TypeVar("T")


def run_supabase_query(query: Callable[[], T]) -> T:
    try:
        return query()
    except APIError as exc:
        raise_supabase_http_error(exc)
