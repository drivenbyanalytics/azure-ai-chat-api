from fastapi import Request
from fastapi.responses import JSONResponse

from models.models import ErrorResponse


class FileValidationError(Exception):
    pass


class FileProcessingError(Exception):
    pass


class DatabaseError(Exception):
    pass


class SearchIndexingError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


def register_exception_handlers(app):
    def build_response(exc: Exception, code: str = None):
        return ErrorResponse(detail=str(exc), code=code).model_dump()

    @app.exception_handler(FileValidationError)
    async def file_validation_exception_handler(
        request: Request, exc: FileValidationError
    ):
        return JSONResponse(
            status_code=422, content=build_response(exc, code="FILE_VALIDATION_ERROR")
        )

    @app.exception_handler(FileProcessingError)
    async def file_processing_exception_handler(
        request: Request, exc: FileProcessingError
    ):
        return JSONResponse(
            status_code=500, content=build_response(exc, code="FILE_PROCESSING_ERROR")
        )

    @app.exception_handler(DatabaseError)
    async def database_exception_handler(request: Request, exc: DatabaseError):
        return JSONResponse(
            status_code=500, content=build_response(exc, code="DATABASE_ERROR")
        )

    @app.exception_handler(SearchIndexingError)
    async def search_exception_handler(request: Request, exc: SearchIndexingError):
        return JSONResponse(
            status_code=500, content=build_response(exc, code="SEARCH_INDEXING_ERROR")
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        return JSONResponse(
            status_code=404, content=build_response(exc, code="FILE_NOT_FOUND")
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500, content=build_response(exc, code="INTERNAL_SERVER_ERROR")
        )
