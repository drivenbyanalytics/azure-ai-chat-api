from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.exceptions import register_exception_handlers
from api.routes.file_routes import router as file_router

app = FastAPI(title="File Ingestion API")

# Define allowed origins list
allowed_origins = [
    "http://localhost:4200",
    "https://proud-desert-05f33aa03.1.azurestaticapps.net",
    "https://proud-desert-05f33aa03-4.westeurope.1.azurestaticapps.net",
    "https://proud-desert-05f33aa03-*.westeurope.1.azurestaticapps.net"
]

# Add CORS middleware with origins list
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register centralized exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(file_router)
