from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

# Define Item class inheriting from Base
# This stores information on items itself
class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))

    transactions = relationship("Transaction", back_populates="item")
    stocks = relationship("Stock", back_populates="item")


# Define Store class inheriting from Base
# This stores information on the store itself
# This is used for transactions.
class Store(Base):
    __tablename__ = "store"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))

    transactions = relationship("Transaction", back_populates="store")
    stocks = relationship("Stock", back_populates="store")


# Define Transaction class inheriting from Base
# This stores information on the transaction itself
# Multiple rows can be part of the same transaction.
# I have yet to work out how to deal with price over a single full transaction.
# NOTE: Price is handled in pennies. To keep it as a juicy integer.
# TODO: Remove all info, about store, item, quantity. That's for stock DB.
class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    item_id = Column(Integer, ForeignKey("item.id"))
    store_id = Column(Integer, ForeignKey("store.id"))
    price = Column(Integer)
    quantity = Column(Integer)

    item = relationship("Item", back_populates="transactions")
    store = relationship("Store", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")


# Define Stock class inheriting from Base
# This tracks anytime stock changes at any store
# Can add stock
# Can remove stock
# Stock is removed when a transaction happens
# Transactions are tied to stock change
class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"))
    store_id = Column(Integer, ForeignKey("store.id"))
    quantity = Column(Integer)

    item = relationship("Item", back_populates="stocks")
    store = relationship("Store", back_populates="stocks")
    # NOTE SINGULAR, NOT PLURAL
    transaction = relationship("Transaction", back_populates="stock")
