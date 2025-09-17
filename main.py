from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from models.response_models import UploadFileResponse, ErrorResponse, ListFilesResponse, DeleteFileResponse
from services.ingestion_pipeline import IngestionPipeline
from services.cosmos_service import CosmosService
from services.exceptions import FileNotFoundError

app = FastAPI()


@app.post(
    "/upload-file", 
    response_model=UploadFileResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def upload_file(file: UploadFile = File(...)):
    # Allow .txt and .pdf files
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=422, detail="Only .txt files are supported")

    try:
        pipeline = IngestionPipeline()

        content_bytes = await file.read()
        if file.filename.endswith(".txt"):
            content = content_bytes.decode("utf-8")
        else:
            content = content_bytes  # Implement PDF parser later

        result = pipeline.process_file(file.filename, content)

        return JSONResponse(content={**result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/files",
    response_model=ListFilesResponse,
    responses={500: {"model": ErrorResponse}}
)
async def list_files():
    """
    List all stored files in Cosmos DB.
    """
    try:
        cosmos_service = CosmosService()
        files = cosmos_service.list_files()
        return JSONResponse(content={"files": files}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(
    "/files/{file_id}",
    response_model=DeleteFileResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def delete_file(file_id: str):
    """
    Delete a file from Cosmos DB by its ID.
    """
    try:
        cosmos_service = CosmosService()
        deleted = cosmos_service.delete_file(file_id)
        return DeleteFileResponse(file_id=file_id, deleted=deleted)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
