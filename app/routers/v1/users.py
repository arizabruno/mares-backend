from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import *
from app.schemas.movie import *
from app.data_access.queries import *
from dotenv import load_dotenv
import os
from app.data_access.queries import *

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("", response_description="Create a new user", response_model=UserCreate)
async def create_user_endpoint(user: UserCreate):
    """
    Create a new user with email, username, full name, and hashed password.
    """
    result = create_user(user.email, user.username, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="User could not be created.")
    return user

@router.get("", response_description="Read all users")
async def read_all_users_endpoint():
    """
    Read and return all users.
    """
    users = read_all_users()
    if users is None:
        raise HTTPException(status_code=404, detail="No users found.")
    return users

@router.get("/{user_id}", response_description="Read a user by ID")
async def read_user_by_id_endpoint(token: Annotated[str, Depends(oauth2_scheme)], user_id: int):
    """
    Read and return a user by their ID.
    
    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
    - user_id (int): The user's id.

    Returns:
    - dict: TODO

    Raises:
    - HTTPException: If the operation fails.
    """
    user = read_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.put("/{user_id}", response_description="Update a user's information")
async def update_user_info_endpoint(token: Annotated[str, Depends(oauth2_scheme)], user_id: int, user: UserUpdate):
    """
    Update a user's email, username, full name, or hashed password.
    
    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
    - user_id (int): The user's id.
    - user (UserUpdate): The content to be updated.
    
    Returns:
    - dict: A message indicating the outcome of the operation.

    Raises:
    - HTTPException: If the operation fails.
    """
    success = update_user_info(user_id, user.new_email, user.new_username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="User update failed.")
    return {"message": "User updated successfully."}

@router.delete("/{user_id}", response_description="Delete a user")
async def delete_user_endpoint(token: Annotated[str, Depends(oauth2_scheme)], user_id: int):
    """
    Delete a user by their ID.
    
    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
    - user_id (int): The user's id.
    
    Returns:
    - dict: A message indicating the outcome of the operation.

    Raises:
    - HTTPException: If the operation fails.
    """
    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="User deletion failed.")
    
    return {"message": "User deleted successfully."}
