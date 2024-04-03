from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.logic import authenticate_user, create_access_token
from app.data_access.queries import *
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers import v1
from app.routers.v1 import movies as v1_movies_routes
from app.routers.v1 import users as v1_users_routes

from app.schemas.token import Token

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Application Initialization
app = FastAPI()


# CORS Configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)

@app.post("/token", response_model=Token, tags=["Auth"])
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
    

app.include_router(
    v1_users_routes.router,
    prefix="/api/v1/users",
    tags=["v1", "users"]
)


app.include_router(
    v1_movies_routes.router,
    prefix="/api/v1/movies",
    tags=["v1", "movies"]
)
