from fastapi import FastAPI

from api.exceptions import register_exception_handlers
from api.routes.file_routes import router as file_router

app = FastAPI(title="File Ingestion API")

# Register centralized exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(file_router)
