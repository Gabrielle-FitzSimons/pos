import codecs
import csv
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
import logging
import math

from typing import List, Optional
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Response,
    status,
    UploadFile,
    File,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.timing import add_timing_middleware
from database import Base, engine, get_session, SessionLocal
from sqlalchemy.orm import Session

import models
import schemas
from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    check_superuser,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
import utils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database
Base.metadata.create_all(engine)

# Initialize app
app = FastAPI()
add_timing_middleware(app, record=logger.info, prefix="app")

# origins = ["http://localhost", "http://localhost:3000", "http://localhost:8080", "*"]
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://pos.vapexstores.co.uk",
    "https://pos.vapexstores.co.uk",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # get the item item with the given id
    user = (
        session.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not authenticate_user(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # logger.info("ACCESS TOKEN:")
    # logger.info(access_token)
    return access_token


@app.post("/users", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    check_superuser(current_user)

    password_hash = get_password_hash(user.password)

    userdb = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=False,
        hashed_password=password_hash,
    )

    # add it to the session and commit it
    session.add(userdb)
    session.commit()
    session.refresh(userdb)

    # return the item object
    return userdb


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users", response_model=List[schemas.User])
def read_user_list(
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    check_superuser(current_user)

    # get all users
    user_list = session.query(models.User).all()

    return user_list


@app.post("/item", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # create an instance of the Item database model
    itemdb = models.Item(name=item.name)

    # add it to the session and commit it
    session.add(itemdb)
    session.commit()
    session.refresh(itemdb)

    # return the item object
    return itemdb


@app.get("/item/{id}", response_model=schemas.Item)
def read_item(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the item item with the given id
    item = session.query(models.Item).get(id)

    # check if item item with given id exists. If not, raise exception and return 404 not found response
    if not item:
        raise HTTPException(status_code=404, detail=f"item item with id {id} not found")

    return item


@app.put("/item/{id}", response_model=schemas.Item)
def update_item(
    id: int,
    name: str,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

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
def delete_item(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
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
def read_item_list(
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get all item items
    item_list = session.query(models.Item).all()

    return item_list


@app.post("/store", response_model=schemas.Store, status_code=status.HTTP_201_CREATED)
def create_store(
    store: schemas.StoreCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # create an instance of the Store database model
    storedb = models.Store(name=store.name)

    # add it to the session and commit it
    session.add(storedb)
    session.commit()
    session.refresh(storedb)

    # return the store object
    return storedb


@app.get("/store/{id}", response_model=schemas.Store)
def read_store(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the store with the given id
    store = session.query(models.Store).get(id)

    # check if store with given id exists. If not, raise exception and return 404 not found response
    if not store:
        raise HTTPException(
            status_code=404, detail=f"store item with id {id} not found"
        )

    return store


@app.put("/store/{id}", response_model=schemas.Store)
def update_store(
    id: int,
    name: str,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

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
def delete_store(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
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
def read_store_list(
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get all store stores
    store_list = session.query(models.Store).all()

    return store_list


@app.post(
    "/transaction",
    response_model=schemas.TransactionShow,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    # create an instance of the Transaction database model
    transactiondb = models.Transaction(
        price=transaction.price,
    )

    for item in transaction.items:
        # Update stock amount
        stockdb = models.Stock(
            item_id=item.item_id,
            store_id=transaction.store_id,
            quantity=item.quantity,
            transaction=transactiondb,
            transaction_id=transactiondb.id,
        )
        session.add(stockdb)

    # add it to the session and commit it
    session.add(transactiondb)
    session.commit()
    session.refresh(transactiondb)
    return read_transaction(transactiondb.id, session)


@app.get("/transaction/{id}", response_model=schemas.TransactionShow)
def read_transaction(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the transaction with the given id
    transaction = session.query(models.Transaction).get(id)

    # check if transaction with given id exists. If not, raise exception and return 404 not found response
    if not transaction:
        raise HTTPException(
            status_code=404, detail=f"transaction item with id {id} not found"
        )

    response = utils.prettify_transaction(transaction)
    return response


@app.put("/transaction/{id}", response_model=schemas.TransactionShow)
def update_transaction(
    id: int,
    transaction: schemas.TransactionUpdate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the transaction with the given id
    transactiondb = session.query(models.Transaction).get(id)

    # check if transaction with given id exists. If not, raise exception and return 404 not found response
    if not transactiondb:
        raise HTTPException(
            status_code=404, detail=f"transaction with id {id} not found"
        )

    transactiondb.price = transaction.price or transactiondb.price

    if transaction.items:
        for item in transactiondb.stocks:
            session.delete(item)
        for item in transaction.items:
            stockdb = models.Stock(
                item_id=item.item_id,
                store_id=transaction.store_id or transactiondb.stock[0].store_id,
                quantity=item.quantity,
                transaction=transactiondb,
                transaction_id=transactiondb.id,
            )
            session.add(stockdb)

    session.commit()
    session.refresh(transactiondb)

    return read_transaction(transactiondb.id, session)


@app.delete(
    "/transaction/{id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_transaction(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Should this method exist??? NO!!!!
    """

    # get the transaction with the given id
    transaction = session.query(models.Transaction).get(id)

    # if transaction with given id exists, delete it from the database. Otherwise raise 404 error
    if transaction:
        for item in transaction.stocks:
            session.delete(item)
        session.delete(transaction)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"transaction with id {id} not found"
        )

    return None


@app.get("/transaction", response_model=List[schemas.TransactionShow])
def read_transaction_custom(
    store_id: Optional[int] = None,
    start_date: Optional[str] = Query(
        default=None, regex="^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    ),
    end_date: Optional[str] = Query(
        default=None, regex="^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    ),
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    This is going to be one BIG BIG DIRTY method for dealing with all custom ranges.
    Can filter through a range of query parameters
    store_id:
    start_date:     INCLUSIVE!
    end_date:       EXCLUSIVE!
    min_price
    max_price
    """
    transaction_list = session.query(models.Transaction)
    if min_price:
        transaction_list = transaction_list.filter(
            models.Transaction.price >= min_price
        )
    if max_price:
        transaction_list = transaction_list.filter(
            models.Transaction.price <= max_price
        )
    if start_date:
        transaction_list = transaction_list.filter(
            models.Transaction.datetime >= start_date
        )
    if end_date:
        transaction_list = transaction_list.filter(
            models.Transaction.datetime <= end_date
        )
    if store_id:
        transaction_list = transaction_list.join(
            models.Stock, models.Transaction.stocks
        ).filter(models.Stock.store_id == store_id)
    response = [
        utils.prettify_transaction(transaction)
        for transaction in transaction_list.all()
    ]
    return response


@app.post("/total/batch", status_code=status.HTTP_201_CREATED)
def create_total(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Takes in a CSV of totals.
    """
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    for row in csvReader:
        date = row["date"]
        card = float(row["card"] or 0)
        cash = float(row["cash"] or 0)
        total = float(row.get("total") or 0)
        store_id = int(row["store_id"])
        transaction_count = int(row["transaction_count"]) or 0

        date = datetime.strptime(date, "%d/%m/%y")
        cash = int(math.ceil(cash * 100))
        card = int(math.ceil(card * 100))
        total = int(math.ceil(total * 100)) if total else cash + card
        if total != cash + card:
            raise HTTPException(
                status_code=404,
                detail=f"total does not equal cash and card for date {date}, store_id {store_id}, cash {cash}, card {card}, total {total}",
            )

        # create an instance of the Store database model
        totaldb = models.Total(
            date=date,
            card=card,
            cash=cash,
            total=total,
            store_id=store_id,
            transaction_count=transaction_count,
        )
        # add it to the session and commit it
        session.add(totaldb)

    session.commit()
    # session.refresh(totaldb)

    # return the store object
    return {"status": "done"}


@app.post("/total", response_model=schemas.Total, status_code=status.HTTP_201_CREATED)
def create_total(
    total: schemas.TotalCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    TODO: FIX THIS. ADD CSV SUPPORT. FIX THE SHITTY BROKEN SYSTEM I HAVE NOW. FUCK THIS SO MUCH.
    """
    cash = int(math.ceil(total.cash * 100))
    card = int(math.ceil(total.card * 100))
    total_input = int(math.ceil(total.total * 100))
    if total_input != cash + card:
        raise HTTPException(
            status_code=404, detail=f"total does not equal cash and card"
        )

    # Check if total already exists
    total_day = read_total_custom(
        total.store_id,
        start_date=str(total.date),
        end_date=str(total.date + timedelta(days=1)),
        session=session,
    )
    if len(total_day) > 0:
        raise HTTPException(status_code=404, detail=f"Total already exists!")

    # create an instance of the Store database model
    totaldb = models.Total(
        date=total.date,
        card=card,
        cash=cash,
        total=total_input,
        store_id=total.store_id,
        transaction_count=total.transaction_count,
    )

    # add it to the session and commit it
    session.add(totaldb)
    session.commit()
    session.refresh(totaldb)

    # return the store object
    return totaldb


@app.get("/total/{id}", response_model=schemas.Total)
def read_total(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the store with the given id
    total = session.query(models.Total).get(id)

    # check if store with given id exists. If not, raise exception and return 404 not found response
    if not total:
        raise HTTPException(
            status_code=404, detail=f"total item with id {id} not found"
        )

    return total


@app.put("/total/{id}", response_model=schemas.Total)
def update_total(
    id: int,
    cash: int = None,
    card: int = None,
    store_id: int = None,
    transaction_count: int = None,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):

    # get the store with the given id
    total = session.query(models.Total).get(id)

    # update store with the given name (if a store with the given id was found)
    total.cash = cash if cash else total.cash
    total.card = card if card else total.card
    total.store_id = total.store_id if store_id else total.store_id
    total.transaction_count = (
        total.transaction_count if transaction_count else total.transaction_count
    )

    session.commit()

    # check if total with given id exists. If not, raise exception and return 404 not found response
    if not total:
        raise HTTPException(status_code=404, detail=f"total with id {id} not found")

    return total


@app.delete("/total/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_total(
    id: int,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Should this method exist???
    """

    # get the store with the given id
    total = session.query(models.Total).get(id)

    # if total with given id exists, delete it from the database. Otherwise raise 404 error
    if total:
        session.delete(total)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"total with id {id} not found")

    return None


# @app.get("/total", response_model=List[schemas.Total])
# def read_total_list(
#     session: Session = Depends(get_session),
#     current_user: schemas.User = Depends(get_current_active_user),
# ):

#     # get all total stores
#     total_list = session.query(models.Total).all()

#     return total_list


@app.get("/total", response_model=List[schemas.Total])
def read_total_custom(
    store_id: Optional[int] = None,
    start_date: Optional[str] = Query(
        default=None, regex="^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    ),
    end_date: Optional[str] = Query(
        default=None, regex="^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    ),
    week: Optional[bool] = False,
    ascending: Optional[bool] = False,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    This is going to be one BIG BIG DIRTY method for dealing with all custom ranges.
    Can filter through a range of query parameters
    store_id:
    start_date:     INCLUSIVE!
    end_date:       EXCLUSIVE!
    min_price
    max_price
    """

    def store_grouper(item):
        store_id = item.store_id
        return store_id

    def week_grouper(item):
        item_date = item.date.date()
        week = item_date.isocalendar().week
        return week

    def month_grouper(item):
        item_date = item.date.date()
        month = item_date.isocalendar().month
        return month

    total_list = session.query(models.Total)
    if start_date:
        total_list = total_list.filter(models.Total.date >= start_date)
    if end_date:
        total_list = total_list.filter(models.Total.date <= end_date)
    if store_id:
        total_list = total_list.filter(models.Total.store_id == store_id)

    result = total_list.order_by(models.Total.date).all()

    if week:
        # Groups by week.
        # If store_id not given, collates all stores result.
        final_result = []
        for (week, items) in groupby(result, week_grouper):
            sorted_items = sorted(items, key=lambda item: item.store_id)
            for (_store_id, sub_items) in groupby(sorted_items, store_grouper):
                total = 0
                card_total = 0
                cash_total = 0
                transaction_total = 0
                starting_date = None
                tran_id = None
                store_id = None
                for item in sub_items:
                    tran_id = tran_id or item.id
                    starting_date = starting_date or item.date
                    card_total += item.card
                    cash_total += item.cash
                    transaction_total += item.transaction_count
                    store_id = store_id or item.store_id
                total += cash_total + card_total
                final_result.append(
                    {
                        "id": tran_id,
                        "store_id": store_id or -1,
                        "date": starting_date,
                        "total": total,
                        "card": card_total,
                        "cash": cash_total,
                        "transaction_count": transaction_total,
                    }
                )
        result = final_result

    if not ascending:
        result.reverse()

    return result
