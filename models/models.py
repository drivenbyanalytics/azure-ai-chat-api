from typing import ClassVar, List, Optional

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

class ChunkMetadata(BaseModel):
    """Metadata for document chunks in the vector store."""
    chunk_id: str = Field(..., description="Unique ID of the chunk")
    file_id: str = Field(..., description="ID of the file this chunk belongs to")
    created_at: str = Field(..., description="ISO timestamp when the chunk was created")


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


class TokenResponse(BaseModel):
    access_token: str = Field(
        ..., description="JWT access token for authenticated requests"
    )
    token_type: str = Field(
        "bearer", description="Type of the token, typically 'bearer'"
    )


# Chat completion models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question or message")
    chat_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous chat messages")


class ContextInfo(BaseModel):
    content: str = Field(..., description="Snippet of the context content")
    file_id: str = Field(..., description="ID of the file this context came from")
    score: float = Field(..., description="Relevance score of the context")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    timestamp: str = Field(..., description="ISO timestamp of the response")
