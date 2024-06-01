from fastapi import HTTPException
from sqlmodel import Session

from app.models import Users
from app.repository.tag_repository import TagRepository
from app.repository.transaction_repository import TransactionRepository
from app.schemas import (
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionType,
    TransactionSummary,
)
from app.utils.date_utils import DateUtils


class TransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.transaction_repository = TransactionRepository(session)
        self.tag_repository = TagRepository(session)

    def create_transaction(self, transaction: TransactionCreate, current_user: Users):
        if transaction.tag_id:
            self.tag_repository.get_tag_by_id(transaction.tag_id)

        return self.transaction_repository.create_transaction(
            transaction, current_user.id
        )

    def get_transactions(self, year_month: str, current_user: Users):
        first_day_of_month, last_day_of_month = (
            DateUtils.get_first_last_date_from_year_month(year_month)
        )

        return self.transaction_repository.get_transactions_by_date_between(
            current_user.id, first_day_of_month, last_day_of_month
        )

    def get_months_with_transactions(self, current_user: Users):
        months_with_transactions = (
            self.transaction_repository.find_months_with_transactions(current_user.id)
        )

        response = [
            TransactionFormattedMonthsWithTransactions(
                date=f"{date.year}-{date.month:02d}",
                formattedDate=DateUtils.get_formatted_date(
                    f"{date.year}-{date.month:02d}"
                ),
            )
            for date in months_with_transactions
        ]

        return response

    def get_transaction_summary(self, year_month: str, current_user: Users):
        first_day_of_month, last_day_of_month = (
            DateUtils.get_first_last_date_from_year_month(year_month)
        )
        transactions = self.transaction_repository.get_transactions_by_date_between(
            current_user.id, first_day_of_month, last_day_of_month
        )

        outcome_transactions = filter(
            lambda transaction: transaction.type == TransactionType.OUTCOME,
            transactions,
        )
        income_transactions = filter(
            lambda transaction: transaction.type == TransactionType.INCOME, transactions
        )

        total_outcome = sum(transactions.value for transactions in outcome_transactions)
        total_income = sum(transactions.value for transactions in income_transactions)
        profit = total_income - total_outcome

        summary = TransactionSummary(
            formattedDate=DateUtils.get_formatted_date(year_month),
            initialDate=first_day_of_month,
            lastDate=last_day_of_month,
            totalOutcome=total_outcome,
            totalIncome=total_income,
            profit=profit,
        )

        return summary

    def delete_transaction(
        self,
        current_user: Users,
        transaction_id: int,
    ):
        transaction = self.transaction_repository.get_transaction_by_id(transaction_id)

        if transaction.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Transaction not found!")

        self.transaction_repository.delete_transaction(transaction_id)
