from fastapi import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import JSONResponse

from models.models import ErrorResponse


class FileValidationError(Exception):
    """Raised when file validation fails."""

    pass


class FileProcessingError(Exception):
    """Raised when error happens during file processing."""

    pass


class DatabaseError(Exception):
    """Raised when db related error happens."""

    pass


class SearchIndexingError(Exception):
    """Raised when search index related error happens."""

    pass

class ChatCompletionError(Exception):
    """Raised when error happens during chat completion."""

    pass


class FileNotFoundError(Exception):
    """Raised when file not found."""

    pass


class AuthenticationError(Exception):
    """Raised when username or password is invalid during login."""

    pass


class AuthorizationError(Exception):
    """Raised when a token is missing, invalid, or expired."""

    pass


def register_exception_handlers(app):
    def build_response(
        exc: Exception, code: str, status: str = "error", message: str = None
    ):
        return ErrorResponse(
            status=status, code=code, message=message or str(exc)
        ).model_dump()

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
    
    @app.exception_handler(ChatCompletionError)
    async def chat_exception_handler(request: Request, exc: ChatCompletionError):
        return JSONResponse(
            status_code=500, content=build_response(exc, code="CHAT_COMPLETION_ERROR")
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

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        messages = "; ".join(
            [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
        )
        return JSONResponse(
            status_code=422,
            content=build_response(exc, code="VALIDATION_ERROR", message=messages),
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(
        request: Request, exc: AuthenticationError
    ):
        return JSONResponse(
            status_code=401,
            content=build_response(exc, code="AUTHENTICATION_ERROR"),
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(
        request: Request, exc: AuthorizationError
    ):
        return JSONResponse(
            status_code=401,
            content=build_response(exc, code="AUTHORIZATION_ERROR"),
        )
