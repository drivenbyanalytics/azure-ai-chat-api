from fastapi import APIRouter, File, Path, UploadFile

from exceptions import FileValidationError
from models.models import (
    DeleteFileResponse,
    ErrorResponse,
    FileMetadata,
    GetFileResponse,
    ListFilesResponse,
    UploadFileResponse,
)
from services.cosmos_service import CosmosService
from services.ingestion_pipeline import IngestionPipeline

router = APIRouter()
pipeline = IngestionPipeline()
cosmos_service = CosmosService()


@router.post(
    "/upload-file",
    response_model=UploadFileResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_file(file: UploadFile = File(...)):
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise FileValidationError("Only .txt and .pdf files are supported")

    content_bytes: bytes = await file.read()
    content: str = (
        content_bytes.decode("utf-8")
        if file.filename.endswith(".txt")
        else content_bytes
    )

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
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_file(
    file_id: str = Path(..., description="The ID of the file to delete")
):
    success = cosmos_service.delete_file(file_id)
    return DeleteFileResponse(file_id=file_id, deleted=success)
