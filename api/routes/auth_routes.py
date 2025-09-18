from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from models.models import ErrorResponse, TokenResponse
from services.auth_service import AuthService
from settings import settings

router = APIRouter()
auth_service = AuthService()


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return a bearer token.
    """
    auth_service.validate_user(form_data.username, form_data.password)
    access_token = auth_service.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
