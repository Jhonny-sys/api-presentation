import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    supabase_url: str
    supabase_service_key: str
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10
    jwt_refresh_expire_days: int = 7
    refresh_token_pepper: str
    api_client_secret: str

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_supabase_key(self) -> None:
        key = self.supabase_service_key

        if key.startswith("sb_secret_") or key.startswith("eyJ"):
            return

        if key.startswith("sb_publishable_"):
            logger.warning(
                "SUPABASE_SERVICE_KEY parece ser la publishable key. "
                "El backend necesita la SECRET key (sb_secret_...) desde Supabase → Settings → API Keys."
            )
            return

        logger.warning(
            "SUPABASE_SERVICE_KEY no está configurada correctamente. "
            "Copia la Secret key desde Supabase → Settings → API Keys → Secret keys → default. "
            "Formato nuevo: sb_secret_... | Legacy: eyJ..."
        )


settings = Settings()
settings.validate_supabase_key()
