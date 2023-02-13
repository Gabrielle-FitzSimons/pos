import datetime

from pydantic import BaseModel
from typing import List, Optional

# Create Item Schema (Pydantic Model)
class ItemCreate(BaseModel):
    name: str


# Complete Item Schema (Pydantic Model)
class Item(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# Create Store Schema (Pydantic Model)
class StoreCreate(BaseModel):
    name: str


# Complete Store Schema (Pydantic Model)
class Store(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# Show Single Stock Change
class Stock(BaseModel):
    id: int
    item_id: int
    store_id: int
    transaction_id: int
    quantity: int

    class Config:
        orm_mode = True


# Create Transaction Schema (Pydantic Model)
class TransactionSingleCreate(BaseModel):
    item_id: int
    quantity: int


# Create Transaction Schema (Pydantic Model)
class TransactionCreate(BaseModel):
    items: List[TransactionSingleCreate]
    store_id: int
    price: int


# Showw Full Transaction
class TransactionShow(BaseModel):
    id: int
    items: List[Stock]
    store_id: int
    price: int
    datetime: datetime.datetime

    class Config:
        orm_mode = True


# Update Transaction Schema (Pydantic Model)
class TransactionUpdate(BaseModel):
    items: Optional[List[TransactionSingleCreate]]
    store_id: Optional[int]
    price: Optional[int]


# Complete Store Schema (Pydantic Model)
class Transaction(BaseModel):
    id: int
    datetime: datetime.datetime
    price: int

    class Config:
        orm_mode = True


# For authentication
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool

    class Config:
        orm_mode = True


class UserCreate(User):
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expiry: datetime.datetime


class TokenData(BaseModel):
    username: str
