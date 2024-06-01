from datetime import date

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Transaction
from app.schemas import TransactionCreate, TransactionMonthsWithTransactions


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_transaction(self, transaction: TransactionCreate, user_id: int):
        db_transaction = Transaction.model_validate(
            transaction, update={"user_id": user_id}
        )

        self.session.add(db_transaction)
        self.session.commit()
        self.session.refresh(db_transaction)

        return db_transaction

    def get_transactions_by_date_between(
        self, user_id: int, initial_date: date, end_date: date
    ):
        search_transactions = (
            select(Transaction)
            .where(Transaction.transaction_date >= initial_date)
            .where(Transaction.transaction_date <= end_date)
            .where(Transaction.user_id == user_id)
        )

        return self.session.exec(search_transactions).all()

    def get_transaction_by_id(self, transaction_id: int):
        search_transaction = select(Transaction).where(Transaction.id == transaction_id)
        return self.session.exec(search_transaction).first()

    def find_months_with_transactions(self, user_id: int):
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

        search_transactions_result = self.session.execute(search_transactions)
        transaction_months = [
            TransactionMonthsWithTransactions(year=row.year, month=row.month)
            for row in search_transactions_result
        ]

        return transaction_months

    def delete_transaction(self, transaction_id: int):
        search_transaction = select(Transaction).where(Transaction.id == transaction_id)
        transaction = self.session.exec(search_transaction).first()

        self.session.delete(transaction)
        self.session.commit()
