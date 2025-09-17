from fastapi import File, UploadFile

from api.exceptions import FileValidationError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


async def validate_file(file: UploadFile = File(...)) -> UploadFile:
    # Validate extension
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise FileValidationError(
            f"Only {', '.join(ALLOWED_EXTENSIONS)} files are supported"
        )

    # Validate size
    size = 0
    chunk_size = 1024 * 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise FileValidationError(
                f"File size exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit"
            )

    # Reset file pointer for downstream processing
    await file.seek(0)
    return file
