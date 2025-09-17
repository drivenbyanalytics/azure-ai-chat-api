from fastapi import APIRouter, Depends, Path, UploadFile

from api.exceptions import FileValidationError
from models.models import (
    DeleteFileResponse,
    ErrorResponse,
    FileMetadata,
    GetFileResponse,
    ListFilesResponse,
    UploadFileResponse,
)
from services.file_pipeline.cosmos_service import CosmosService
from services.file_pipeline.file_validator import validate_file
from services.file_pipeline.ingestion_pipeline import IngestionPipeline
from services.file_reader.file_reader import FileReader

router = APIRouter()
pipeline = IngestionPipeline()
cosmos_service = CosmosService()
file_reader = FileReader()


@router.post(
    "/upload-file",
    response_model=UploadFileResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_file(file: UploadFile = Depends(validate_file)):
    if not (file.filename.endswith((".txt", ".pdf", ".docx"))):
        raise FileValidationError("Only .txt, .docx and .pdf files are supported")

    content = file_reader.read_file(file)

    result = pipeline.process_file(file.filename, content)
    return UploadFileResponse(**result)


@router.get(
    "/files",
    response_model=ListFilesResponse,
    responses={500: {"model": ErrorResponse}},
)
async def list_files():
    files = cosmos_service.list_files()
    return ListFilesResponse(files=files)


@router.get(
    "/files/{file_id}",
    response_model=GetFileResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_file(
    file_id: str = Path(..., description="The ID of the file to retrieve")
):
    file_item = cosmos_service.get_file(file_id)
    return GetFileResponse(
        file=FileMetadata(
            id=file_item["id"],
            filename=file_item["filename"],
            created_at=file_item["created_at"],
        )
    )


@router.delete(
    "/files/{file_id}",
    response_model=DeleteFileResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def delete_file(
    file_id: str = Path(..., description="The ID of the file to delete")
):
    success = cosmos_service.delete_file(file_id)
    return DeleteFileResponse(file_id=file_id, deleted=success)
