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
    admin_username: str = "admin"
    admin_password: str

    i18n_source_lang: str = "es"
    i18n_target_languages: str = "en,pt"
    translation_api_url: str = "https://api.mymemory.translated.net/get"
    translation_delay_ms: int = 350

    supabase_storage_bucket: str = "portfolio-assets"
    upload_max_files: int = 3
    upload_max_size_mb: int = 5
    upload_allowed_mime_types: str = (
        "image/jpeg,image/png,image/webp,image/gif,application/pdf"
    )

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    chat_max_turns: int = 3
    chat_max_message_chars: int = 500

    @property
    def i18n_target_languages_list(self) -> list[str]:
        langs = [
            lang.strip().lower()
            for lang in self.i18n_target_languages.split(",")
            if lang.strip()
        ]
        return [lang for lang in langs if lang != self.i18n_source_lang.lower()]

    @property
    def i18n_all_languages_list(self) -> list[str]:
        source = self.i18n_source_lang.lower()
        return [source, *self.i18n_target_languages_list]

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_max_size_bytes(self) -> int:
        return self.upload_max_size_mb * 1024 * 1024

    @property
    def upload_allowed_mime_types_list(self) -> set[str]:
        return {
            mime.strip()
            for mime in self.upload_allowed_mime_types.split(",")
            if mime.strip()
        }

    def validate_supabase_key(self) -> None:
        if not self.supabase_service_key:
            logger.warning("SUPABASE_SERVICE_KEY no configurada")


settings = Settings()
settings.validate_supabase_key()
