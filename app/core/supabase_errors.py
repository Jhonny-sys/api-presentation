from postgrest.exceptions import APIError
from fastapi import HTTPException


def raise_supabase_http_error(exc: APIError) -> None:
    details = str(exc)
    message = getattr(exc, "message", details)

    if "Invalid API key" in details or "Invalid API key" in message:
        raise HTTPException(
            status_code=503,
            detail=(
                "Supabase API key inválida. "
                "Usa SUPABASE_SERVICE_KEY desde Supabase → Project Settings → API → service_role. "
                "No uses la contraseña de la base de datos."
            ),
        ) from exc

    raise HTTPException(
        status_code=502,
        detail=f"Error al consultar Supabase: {message}",
    ) from exc
