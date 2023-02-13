# Things that don't really fit anywhere else.
# The beginning of the end of conciseness.
import models
import schemas


def prettify_transaction(transaction: models.Transaction) -> schemas.TransactionShow:
    return {
        "id": transaction.id,
        "store_id": transaction.stocks[0].store_id if transaction.stocks else [],
        "price": transaction.price,
        "items": transaction.stocks,
        "datetime": transaction.datetime,
    }
