from pydantic import BaseModel, Field

class UploadFileResponse(BaseModel):
    file_id: str = Field(..., description="Unique ID assigned to the uploaded file")
    
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message explaining what went wrong")  