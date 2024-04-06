from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

from app.schemas.token import TokenData
from app.schemas.user import UserInfo, User
from app.data_access.queries import *
from app.auth.password import oauth2_scheme, verify_password

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_user(username: str) -> Optional[User]:
    """
    Retrieve a user entity based on the username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Optional[User]: The user object if found, None otherwise.
    """
    user = read_user_by_username(username)
    if "error" in user:
        return None
    return User(**user)


def authenticate_user(username: str, password: str) -> Optional[UserInfo]:
    """
    Authenticate a user by verifying their username and password.

    Args:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        Optional[UserInfo]: The authenticated user object if authentication is successful, False otherwise.
    """
    user = get_user(username)

    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for a user.

    Args:
        data (dict): The payload to encode in the JWT token.
        expires_delta (Optional[timedelta]): The lifespan of the token. Defaults to 15 minutes if None.

    Returns:
        str: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInfo:
    """
    Validate an access token and retrieve the user associated with the token.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.

    Returns:
        User: The user associated with the validated token.

    Raises:
        HTTPException: If token validation fails or the user cannot be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")["username"]
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as error:
        raise credentials_exception

    user = read_user_by_username(token_data.username)
    
    if user is None:
        raise credentials_exception
    return user

