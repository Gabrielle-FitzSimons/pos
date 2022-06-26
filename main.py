import datetime
from statistics import quantiles

from typing import List
from fastapi import FastAPI, status, HTTPException, Depends
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session

import models
import schemas

# Create the database
Base.metadata.create_all(engine)

# Initialize app
app = FastAPI()

# Helper function to get database session
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
def root():
    return "pos"


@app.post("/item", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, session: Session = Depends(get_session)):

    # create an instance of the Item database model
    itemdb = models.Item(name=item.name)

    # add it to the session and commit it
    session.add(itemdb)
    session.commit()
    session.refresh(itemdb)

    # return the item object
    return itemdb


@app.get("/item/{id}", response_model=schemas.Item)
def read_item(id: int, session: Session = Depends(get_session)):

    # get the item item with the given id
    item = session.query(models.Item).get(id)

    # check if item item with given id exists. If not, raise exception and return 404 not found response
    if not item:
        raise HTTPException(status_code=404, detail=f"item item with id {id} not found")

    return item


@app.put("/item/{id}", response_model=schemas.Item)
def update_item(id: int, name: str, session: Session = Depends(get_session)):

    # get the item item with the given id
    item = session.query(models.Item).get(id)

    # update item item with the given name (if an item with the given id was found)
    if item:
        item.name = name
        session.commit()

    # check if item item with given id exists. If not, raise exception and return 404 not found response
    if not item:
        raise HTTPException(status_code=404, detail=f"item item with id {id} not found")

    return item


@app.delete("/item/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(id: int, session: Session = Depends(get_session)):
    """
    Should this method exist???
    """

    # get the item item with the given id
    item = session.query(models.Item).get(id)

    # if item item with given id exists, delete it from the database. Otherwise raise 404 error
    if item:
        session.delete(item)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"item item with id {id} not found")

    return None


@app.get("/item", response_model=List[schemas.Item])
def read_item_list(session: Session = Depends(get_session)):

    # get all item items
    item_list = session.query(models.Item).all()

    return item_list


@app.post("/store", response_model=schemas.Store, status_code=status.HTTP_201_CREATED)
def create_store(store: schemas.StoreCreate, session: Session = Depends(get_session)):

    # create an instance of the Store database model
    storedb = models.Store(name=store.name)

    # add it to the session and commit it
    session.add(storedb)
    session.commit()
    session.refresh(storedb)

    # return the store object
    return storedb


@app.get("/store/{id}", response_model=schemas.Store)
def read_store(id: int, session: Session = Depends(get_session)):

    # get the store with the given id
    store = session.query(models.Store).get(id)

    # check if store with given id exists. If not, raise exception and return 404 not found response
    if not store:
        raise HTTPException(
            status_code=404, detail=f"store item with id {id} not found"
        )

    return store


@app.put("/store/{id}", response_model=schemas.Store)
def update_store(id: int, name: str, session: Session = Depends(get_session)):

    # get the store with the given id
    store = session.query(models.Store).get(id)

    # update store with the given name (if a store with the given id was found)
    if store:
        store.name = name
        session.commit()

    # check if store with given id exists. If not, raise exception and return 404 not found response
    if not store:
        raise HTTPException(status_code=404, detail=f"store with id {id} not found")

    return store


@app.delete("/store/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(id: int, session: Session = Depends(get_session)):
    """
    Should this method exist???
    """

    # get the store with the given id
    store = session.query(models.Store).get(id)

    # if store with given id exists, delete it from the database. Otherwise raise 404 error
    if store:
        session.delete(store)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"store with id {id} not found")

    return None


@app.get("/store", response_model=List[schemas.Store])
def read_store_list(session: Session = Depends(get_session)):

    # get all store stores
    store_list = session.query(models.Store).all()

    return store_list


@app.post(
    "/transaction",
    response_model=schemas.Transaction,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction: schemas.TransactionCreate, session: Session = Depends(get_session)
):
    # create an instance of the Transaction database model
    transactiondb = models.Transaction(
        item_id=transaction.item_id,
        store_id=transaction.store_id,
        price=transaction.price,
        quantity=transaction.quantity,
    )

    # add it to the session and commit it
    session.add(transactiondb)
    session.commit()
    session.refresh(transactiondb)

    # return the transaction object
    return transactiondb


@app.get("/transaction/{id}", response_model=schemas.Transaction)
def read_transaction(id: int, session: Session = Depends(get_session)):

    # get the transaction with the given id
    transaction = session.query(models.Transaction).get(id)

    # check if transaction with given id exists. If not, raise exception and return 404 not found response
    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"transaction item with id {id} not found"
        )

    return transaction


@app.put("/transaction/{id}", response_model=schemas.Transaction)
def update_transaction(
    id: int,
    item_id: int,
    store_id: int,
    price: int,
    quantity: int,
    session: Session = Depends(get_session),
):

    # get the transaction with the given id
    transaction = session.query(models.Transaction).get(id)

    # update transaction with the given name (if a transaction with the given id was found)
    if transaction:
        transaction.item_id = item_id
        transaction.store_id = store_id
        transaction.price = price
        transaction.quantity = quantity
        session.commit()

    # check if transaction with given id exists. If not, raise exception and return 404 not found response
    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"transaction with id {id} not found"
        )

    return transaction


@app.delete("/transaction/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(id: int, session: Session = Depends(get_session)):
    """
    Should this method exist??? NO!!!!
    """

    # get the transaction with the given id
    transaction = session.query(models.Transaction).get(id)

    # if transaction with given id exists, delete it from the database. Otherwise raise 404 error
    if transaction:
        session.delete(transaction)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"transaction with id {id} not found"
        )

    return None


@app.get("/transaction", response_model=List[schemas.Transaction])
def read_transaction_list(session: Session = Depends(get_session)):

    # get all transactions
    transaction_list = session.query(models.Transaction).all()

    return transaction_list
