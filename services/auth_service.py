from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from api.exceptions import AuthenticationError, AuthorizationError
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class AuthService:
    """
    Provides authentication and authorization functionality
    using JWT bearer tokens.
    """

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.auth_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.username = settings.username
        self.password = settings.password

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a signed JWT access token.

        Args:
            data (dict): Payload to include in the token (e.g., {"sub": username}).
            expires_delta (Optional[timedelta]): Optional expiration override.

        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def validate_user(self, username: str, password: str) -> None:
        """
        Validate login credentials.

        Args:
            username (str): Input username.
            password (str): Input password.

        Raises:
            AuthenticationError: If username/password are incorrect.
        """
        if username != self.username or password != self.password:
            raise AuthenticationError("Invalid username or password")

    async def verify_token(self, token: str = Depends(oauth2_scheme)) -> str:
        """
        Verify and decode a JWT token from the Authorization header.

        Args:
            token (str): Bearer token passed via Authorization header.

        Returns:
            str: The username (subject) from the token.

        Raises:
            AuthorizationError: If the token is missing, invalid, or expired.
        """
        if not token:
            raise AuthorizationError("Missing bearer token")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None or username != self.username:
                raise AuthorizationError("Invalid authentication credentials")
            return username
        except JWTError as e:
            raise AuthorizationError(f"Token validation error: {str(e)}")
