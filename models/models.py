from typing import ClassVar, List

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    # Constants (not model fields)
    ID: ClassVar[str] = "id"
    FILENAME: ClassVar[str] = "filename"
    CREATED_AT: ClassVar[str] = "created_at"
    # Model fields
    id: str = Field(..., description="Unique ID of the file in Cosmos DB")
    filename: str = Field(..., description="Original filename")
    created_at: str = Field(
        ..., description="ISO timestamp of when the file was stored"
    )


class SearchDocument(BaseModel):
    chunk_id: str = Field(..., description="Unique ID of the text chunk")
    file_id: str = Field(..., description="ID of the file this chunk belongs to")
    chunk_text: str = Field(..., description="Text of the chunk")
    start_char: int = Field(..., description="Start position of the chunk in the file")
    end_char: int = Field(..., description="End position of the chunk in the file")
    created_at: str = Field(..., description="ISO timestamp when the chunk was created")
    contentVector: List[float] = Field(..., description="Embedding vector of the chunk")


class ChunkedEmbedding(BaseModel):
    chunk_text: str = Field(..., description="Text of the chunk")
    vector: List[float] = Field(..., description="Embedding vector for the chunk")


class ProcessFileResult(BaseModel):
    file_id: str = Field(..., description="Unique ID assigned to the processed file")
    chunks_indexed: int = Field(
        ..., description="Number of text chunks that were indexed"
    )


# Response models
class ErrorResponse(BaseModel):
    status: str = Field(..., description="HTTP status as string, e.g., 'error'")
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")


class UploadFileResponse(BaseModel):
    file_id: str = Field(..., description="Unique ID assigned to the uploaded file")
    chunks_indexed: int = Field(
        ..., description="Number of text chunks that were indexed"
    )


class GetFileResponse(BaseModel):
    file: FileMetadata = Field(..., description="Metadata of the requested file")


class ListFilesResponse(BaseModel):
    files: List[FileMetadata] = Field(..., description="List of stored files")


class DeleteFileResponse(BaseModel):
    file_id: str = Field(..., description="ID of the deleted file")
    deleted: bool = Field(..., description="Whether the file was successfully deleted")
