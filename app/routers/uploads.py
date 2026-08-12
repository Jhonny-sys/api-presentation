from fastapi import APIRouter, Depends, File, UploadFile
from supabase import Client

from app.core.security import verify_access_token
from app.core.supabase import get_supabase_client
from app.schemas.storage import UploadBatchResponse, UploadedFileResponse
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    dependencies=[Depends(verify_access_token)],
)


def get_storage_service(client: Client = Depends(get_supabase_client)) -> StorageService:
    return StorageService(client)


@router.post("", response_model=UploadBatchResponse)
async def upload_files(
    file_1: UploadFile = File(...),
    file_2: UploadFile | None = File(default=None),
    file_3: UploadFile | None = File(default=None),
    service: StorageService = Depends(get_storage_service),
) -> UploadBatchResponse:
    files = [file_1]
    if file_2 is not None:
        files.append(file_2)
    if file_3 is not None:
        files.append(file_3)

    uploaded = service.upload_files(files)
    return UploadBatchResponse(
        files=[UploadedFileResponse(**item) for item in uploaded],
        count=len(uploaded),
    )
