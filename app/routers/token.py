from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth.logic import authenticate_user, create_access_token
from app.schemas.user import *
from app.schemas.movie import *
from app.data_access.queries import *
from dotenv import load_dotenv
import os
from app.data_access.queries import *
from app.schemas.token import Token

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    OAuth2 token endpoint that issues access tokens to users upon successful authentication.

    Args:
        form_data (OAuth2PasswordRequestForm): The username and password provided by the user.

    Returns:
        Token: The access token and token type for the authenticated user.

    Raises:
        HTTPException: If authentication fails due to incorrect username or password.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires =  timedelta(seconds=10)
    access_token = create_access_token(
        data={"user":{"id":user.user_id, "username":user.username, "email":user.email}}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
    