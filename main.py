from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from models.response_models import UploadFileResponse, ErrorResponse
from services.ingestion_pipeline import IngestionPipeline

app = FastAPI()

pipeline = IngestionPipeline()


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
        content_bytes = await file.read()
        if file.filename.endswith(".txt"):
            content = content_bytes.decode("utf-8")
        else:
            content = content_bytes  # Implement PDF parser later

        result = pipeline.process_file(file.filename, content)

        return JSONResponse(content={**result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
