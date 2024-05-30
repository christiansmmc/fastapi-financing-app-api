from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Transaction
from app.schemas import TransactionCreate, TransactionMonthsWithTransactions


def create_transaction(
    session: Session,
    transaction: TransactionCreate,
    user_id: int,
):
    db_transaction = Transaction.model_validate(
        transaction, update={"user_id": user_id}
    )

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)

    return db_transaction


def get_transactions_by_date_between(
    session: Session, user_id: int, initial_date: date, end_date: date
):
    search_transactions = (
        select(Transaction)
        .where(Transaction.transaction_date >= initial_date)
        .where(Transaction.transaction_date <= end_date)
        .where(Transaction.user_id == user_id)
    )

    return session.exec(search_transactions).all()


def get_transaction_by_id(session: Session, transaction_id: int):
    search_transaction = select(Transaction).where(Transaction.id == transaction_id)
    return session.exec(search_transaction).first()


def find_months_with_transactions(session: Session, user_id: int):
    search_transactions = (
        select(
            func.extract("year", Transaction.transaction_date).label("year"),
            func.extract("month", Transaction.transaction_date).label("month"),
        )
        .where(Transaction.transaction_date is not None)
        .where(Transaction.user_id == user_id)
        .group_by(
            func.extract("year", Transaction.transaction_date),
            func.extract("month", Transaction.transaction_date),
        )
        .order_by(
            func.extract("year", Transaction.transaction_date).asc(),
            func.extract("month", Transaction.transaction_date).asc(),
        )
    )

    search_transactions_result = session.execute(search_transactions)
    transaction_months = [
        TransactionMonthsWithTransactions(year=row.year, month=row.month)
        for row in search_transactions_result
    ]

    return transaction_months


def delete_transaction(session: Session, transaction_id: int):
    search_transaction = select(Transaction).where(Transaction.id == transaction_id)
    transaction = session.exec(search_transaction).first()

    session.delete(transaction)
    session.commit()
