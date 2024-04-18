from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.data_access.queries import *
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routers.v1 import movies as v1_movies_routes
from app.routers.v1 import users as v1_users_routes
from app.routers import token as token_routes


# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Application Initialization
app = FastAPI()

version = "v0.9"

@app.get("/")
async def main():
    """
    Redirects to the API documentation page.

    Returns:
    - RedirectResponse: Redirects the client to the API documentation.
    """
    return RedirectResponse(url="/docs")

# CORS Configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)

app.include_router(
    token_routes.router,
    prefix="/token",
    tags=["Auth"]
)

app.include_router(
    v1_users_routes.router,
    prefix="/api/v1/users",
    tags=[version, "users"]
)


app.include_router(
    v1_movies_routes.router,
    prefix="/api/v1/movies",
    tags=[version, "movies"]
)
