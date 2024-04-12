from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.logic import create_access_token, create_reset_password_token, get_current_user
from app.schemas.user import *
from app.schemas.movie import *
from app.data_access.queries import *
from dotenv import load_dotenv
import os
from app.data_access.queries import *
from fastapi_mail import FastMail, MessageSchema, MessageType
import smtplib
from app.schemas.token import Token

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
UI_BASE_URL = os.getenv("UI_BASE_URL")
UI_RESET_PASSWORD_ROUTE = os.getenv("UI_RESET_PASSWORD_ROUTE")
FORGET_PASSWORD_LINK_EXPIRE_MINUTES = int(os.getenv("FORGET_PASSWORD_LINK_EXPIRE_MINUTES"))
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", response_description="Create a new user", response_model=bool)
async def create_user_endpoint(user: UserCreate):
    """
    Create a new user with email, username, full name, and hashed password.
    """
    result = create_user(user.email, user.username, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="User could not be created.")
    return result

@router.get("/", response_description="Read all users",  response_model=List[UserInfo])
async def read_all_users_endpoint():
    """
    Read and return all users.
    """
    users = read_all_users()
    if users is None:
        raise HTTPException(status_code=404, detail="No users found.")
    return users

@router.get("/{user_id}", response_description="Read a user by ID", response_model=UserInfo)
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
async def update_user_info_endpoint(current_user: Annotated[UserInfo, Depends(get_current_user)], user: UserUpdate):
    """
    Update a user's email, username, full name, or hashed password.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
    - user_id (int): The user's id.
    - user (UserUpdate): The content to be updated.

    Returns:
    - A new access token.

    Raises:
    - HTTPException: If the operation fails.
    """
    current_user = UserInfo(**current_user)

    success = update_user_info(current_user.user_id, user.email, user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="User update failed.")

    access_token_expires =  timedelta(days=1)
    access_token = create_access_token(
        data={"user":{"id":current_user.user_id, "username":user.username, "email":user.email}}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.delete("/{user_id}", response_description="Delete a user", response_model=bool)
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

    return True


# @router.post("/forgot-password", response_description="Request a password reset", response_model=bool)
# async def forgot_password_endpoint(background_tasks: BackgroundTasks, email: str):
#     """
#     Request a password reset for a user.

#     Parameters:
#     - email (str): The user's email.

#     Returns:
#     - dict: A message indicating the outcome of the operation.

#     Raises:
#     - HTTPException: If the operation fails.
#     """

#     try:
#         user = read_user_by_email(email)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found.")

#         token = create_reset_password_token({"sub": user["email"]})

#         forget_url_link =  f"{UI_BASE_URL}{UI_RESET_PASSWORD_ROUTE}/{token}"

#         email_body = { "link_expiry_min": FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
#                     "reset_link": forget_url_link }

#         template = """
#                     <html>
#                     <body>


#                     <p>Hi !!!
#                     <br>Thanks for using fastapi mail, keep using it..!!!</p>


#                     </body>
#                     </html>
#                     """

#         message = MessageSchema(
#             subject="Fastapi-Mail module",
#             recipients=["aziradev@gmail.com"],
#             body=template,
#             subtype="html"
#             )


#         fm = FastMail(email_conf)
#         await fm.send_message(message)
#         print(message)

#         return True

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Email not sent.")


@router.get("/send-test-email/")
async def send_test_email():
    smtp_server = 'in-v3.mailjet.com'
    smtp_port = 587
    smtp_username = '688929338a2a2f8024eed6d0507aefa6'
    smtp_password = "a708e70638adae6aaf0bf6352ff3d528"

    from_email = 'mares.sys@mail.com'
    to_email = 'aziradev@gmail.com'
    subject = 'Hello, world!'
    body = 'This is a test email.'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)
