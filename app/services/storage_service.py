import mimetypes
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from supabase import Client

from app.core.config import settings


class StorageService:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._bucket = settings.supabase_storage_bucket

    def upload_files(self, files: list[UploadFile]) -> list[dict]:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes enviar al menos un archivo",
            )

        if len(files) > settings.upload_max_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Máximo {settings.upload_max_files} archivos por solicitud",
            )

        uploaded: list[dict] = []
        for file in files:
            uploaded.append(self._upload_single(file))

        return uploaded

    def _upload_single(self, file: UploadFile) -> dict:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido",
            )

        content = file.file.read()
        size = len(content)

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo vacío: {file.filename}",
            )

        if size > settings.upload_max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Archivo muy grande: {file.filename}",
            )

        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if content_type not in settings.upload_allowed_mime_types_list:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Tipo no permitido: {file.filename}",
            )

        storage_path = self._build_storage_path(file.filename)
        storage = self._client.storage.from_(self._bucket)

        try:
            storage.upload(
                path=storage_path,
                file=content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false",
                },
            )
        except Exception as exc:
            if self._is_missing_bucket_error(exc):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Storage no configurado. Ejecuta 005_storage_bucket.sql",
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo subir: {file.filename}",
            ) from exc

        public_url = storage.get_public_url(storage_path)

        return {
            "filename": file.filename,
            "path": storage_path,
            "url": public_url,
            "content_type": content_type,
            "size": size,
        }

    @staticmethod
    def _build_storage_path(original_filename: str) -> str:
        suffix = Path(original_filename).suffix.lower()
        date_prefix = datetime.now(UTC).strftime("%Y/%m/%d")
        unique_name = f"{uuid.uuid4().hex}{suffix}"
        return f"{date_prefix}/{unique_name}"

    @staticmethod
    def _is_missing_bucket_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "bucket" in message and ("not found" in message or "does not exist" in message)
