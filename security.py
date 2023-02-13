from datetime import datetime, timedelta
from typing import Union
import os
import logging

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_session
import models
import schemas


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
# Currently set at 12 hours. Covers working day.
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12


# fake_users_db = {
#     "josh": {
#         "username": "josh",
#         "full_name": "Joshua Wharton",
#         "email": "joshua@vapexstores.co.uk",
#         "hashed_password": "$2b$12$Oe8WaP1s4wHuoZq/EkkUHO.mvlu1dS/naFCEo0VtGuTeAvK6rUMMS",
#         "disabled": False,
#     }
# }


def get_user(session, username: str):
    user = session.query(models.User).filter(models.User.username == username).first()

    if user:
        return schemas.User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            disabled=user.disabled,
        )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(user: schemas.UserInDB, password: str):
    if not verify_password(password, user.hashed_password):
        return False
    return True


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer", "expiry": expire}


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    start = datetime.now()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    end = datetime.now()
    # print(end - start)
    return user


# def get_current_active_user():
#     # def get_current_active_user(
#     #     current_user: schemas.User = Depends(get_current_user),
#     # ):
#     # if current_user.disabled:
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     # return current_user
#     return True
def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
    # return True


def check_superuser(user: schemas.User):
    if not user.username == "josh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are unauthorised to create a new user.",
        )
