from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    """
    Schema for user creation requests.

    Attributes:
        username (str): The unique identifier for the user. Must be a non-empty string.
        password (str): The user's password. This should be received in a secure manner and hashed before storage.
        email (EmailStr): The user's email address. Must be a valid email format.
    """
    username: str
    password: str
    email: EmailStr


class UserUpdate(BaseModel):
    """
    Schema for updating existing user details.

    Attributes:
        username (Optional[str]): New username for the user. Defaults to None, indicating no change.
        password (Optional[str]): New password for the user. Defaults to None, indicating no change.
        email (Optional[EmailStr]): New email address for the user. Defaults to None, indicating no change.
    """
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None


class User(BaseModel):
    """
    Schema representing a user entity.

    Attributes:
        username (str): The user's username. Unique across all users.
        hashed_password (Optional[str]): The user's hashed password. Defaults to None.
            This field is optional to accommodate scenarios where user data is returned without exposing password information.
        email (EmailStr): The user's email address. Must be a valid email format.
    """
    username: str
    hashed_password: Optional[str] = None
    email: EmailStr
