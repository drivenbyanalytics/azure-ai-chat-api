from fastapi import FastAPI

from api.exceptions import register_exception_handlers
from api.routes.auth_routes import router as auth_router
from api.routes.file_routes import router as file_router
from api.routes.chat_routes import router as chat_router

app = FastAPI(title="File Ingestion API")

# Register centralized exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(file_router, tags=["Files"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(chat_router)
