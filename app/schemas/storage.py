from pydantic import BaseModel


class UploadedFileResponse(BaseModel):
    filename: str
    path: str
    url: str
    content_type: str
    size: int


class UploadBatchResponse(BaseModel):
    files: list[UploadedFileResponse]
    count: int
