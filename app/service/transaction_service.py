from datetime import datetime

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.models import Users
from app.repository.tag_repository import TagRepository
from app.repository.transaction_repository import TransactionRepository
from app.schemas import (
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionType,
    TransactionSummary,
    TransactionUpdate,
)
from app.utils.date_utils import DateUtils


def get_tag_name_by_nubank_category_name(nubank_category_name):
    tag_name = ""

    match nubank_category_name:
        case "supermercado":
            tag_name = "Mercado"
        case "restaurante":
            tag_name = "Restaurante"
        case "casa":
            tag_name = "Casa"
        case "saúde":
            tag_name = "Academia e Saúde"
        case "transporte":
            tag_name = "Transporte"
        case "lazer":
            tag_name = "Lazer e Entretenimento"
        case _:
            tag_name = "Outros"

    return tag_name


def get_bank_name_and_date_from_csv_file(csv_filename: str):
    csv_base_name = csv_filename.rsplit(".", 1)[0]
    parts = csv_base_name.split("-")

    bank_name = parts[0]
    date = parts[1] + "-" + parts[2]
    date_format = "%Y-%m"

    transaction_date = datetime.strptime(date, date_format)

    return bank_name, transaction_date


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

    def update_transaction(self, transaction: TransactionUpdate, current_user: Users):
        transaction_to_update = self.get_transaction_by_id(transaction.id, current_user)

        if transaction.tag_id:
            self.tag_repository.get_tag_by_id(transaction.tag_id)

        transaction_to_update.name = transaction.name
        transaction_to_update.description = transaction.description
        transaction_to_update.value = transaction.value
        transaction_to_update.transaction_date = transaction.transaction_date
        transaction_to_update.type = transaction.type
        transaction_to_update.tag_id = transaction.tag_id

        return self.transaction_repository.update_transaction(transaction_to_update)

    def create_transactions_from_csv(
        self,
        csv_file: UploadFile,
        current_user: Users,
    ):
        transaction_to_create = []

        bank_name, transaction_date = get_bank_name_and_date_from_csv_file(
            csv_file.filename
        )

        df = pd.read_csv(csv_file.file)

        for index, row in df.iterrows():
            if row["category"] == "payment":
                continue

            transaction = {
                "name": row["title"],
                "description": f"Importado pelo {bank_name.capitalize()}",
                "value": row["amount"],
                "transaction_date": transaction_date,
                "type": TransactionType.OUTCOME,
            }

            tag_name = get_tag_name_by_nubank_category_name(row["category"])
            if tag_name:
                tag = self.tag_repository.get_tag_by_name(tag_name)
                transaction["tag_id"] = tag.id

            transaction_to_create.append(transaction)

        self.transaction_repository.create_transactions_from_csv(
            transaction_to_create, current_user.id
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
        transaction = self.get_transaction_by_id(transaction_id, current_user)
        self.transaction_repository.delete_transaction(transaction.id)

    def get_transaction_by_id(self, id: int, current_user):
        transaction = self.transaction_repository.get_transaction_by_id(id)

        if transaction.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Transaction not found!")

        return transaction
