import datetime

from pydantic import BaseModel

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


# Create Store Schema (Pydantic Model)
class TransactionCreate(BaseModel):
    item_id: int
    store_id: int
    price: int
    quantity: int


# Complete Store Schema (Pydantic Model)
class Transaction(BaseModel):
    id: int
    datetime: datetime.datetime
    item_id: int
    store_id: int
    price: int
    quantity: int

    class Config:
        orm_mode = True
