from pydantic import BaseModel, Field
from typing import List

class UploadFileResponse(BaseModel):
    file_id: str = Field(..., description="Unique ID assigned to the uploaded file")
    chunks_indexed: int = Field(..., description="Number of text chunks that were indexed")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message explaining what went wrong")

class FileMetadata(BaseModel):
    id: str = Field(..., description="Unique ID of the file in Cosmos DB")
    filename: str = Field(..., description="Original filename")
    created_at: str = Field(..., description="ISO timestamp of when the file was stored")

class ListFilesResponse(BaseModel):
    files: List[FileMetadata] = Field(..., description="List of stored files")

class DeleteFileResponse(BaseModel):
    file_id: str = Field(..., description="ID of the deleted file")
    deleted: bool = Field(..., description="Whether the file was successfully deleted")
