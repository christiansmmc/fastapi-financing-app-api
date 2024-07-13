import base64
import csv
from datetime import datetime
from io import StringIO

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.models import Users
from app.repository.tag_repository import TagRepository
from app.repository.transaction_repository import TransactionRepository
from app.schemas import (
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionImportCsv,
    TransactionType,
    TransactionSummary,
    TransactionUpdate,
)
from app.utils.date_utils import DateUtils

EXPORT_CSV_HEADER = ["Nome", "Valor", "Descricao", "Data", "Tipo", "Categoria"]


def get_tag_name_by_nubank_category_name(nubank_category_name):
    category_map = {
        "supermercado": "Mercado",
        "restaurante": "Restaurante",
        "casa": "Casa",
        "saúde": "Academia e Saúde",
        "transporte": "Transporte",
        "lazer": "Lazer e Entretenimento",
    }
    return category_map.get(nubank_category_name, "Outros")


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
        transaction_import_csv: TransactionImportCsv,
        current_user: Users,
    ):
        transaction_to_create = []

        transaction_date = datetime.strptime(
            transaction_import_csv.transactions_date, "%Y-%m"
        )

        decoded_csv = base64.b64decode(transaction_import_csv.csv_base64).decode(
            "utf-8"
        )
        df = pd.read_csv(StringIO(decoded_csv))

        for index, row in df.iterrows():
            if row["category"] == "payment":
                continue

            transaction = {
                "name": row["title"],
                "description": f"Importado pelo {transaction_import_csv.bank_name.capitalize()}",
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

    def export_transactions_csv(self, year_month: str, current_user: Users):
        first_day_of_month, last_day_of_month = (
            DateUtils.get_first_last_date_from_year_month(year_month)
        )

        transactions = self.transaction_repository.get_transactions_by_date_between(
            current_user.id, first_day_of_month, last_day_of_month
        )

        with StringIO() as csv_buffer:
            csv_writer = csv.writer(csv_buffer)
            csv_writer.writerow(EXPORT_CSV_HEADER)
            for transaction in transactions:
                row = [
                    transaction.name,
                    transaction.value,
                    transaction.description,
                    transaction.transaction_date,
                    transaction.type,
                    transaction.tag.name,
                ]
                csv_writer.writerow(row)
            csv_content = csv_buffer.getvalue()

        csv_content = csv_buffer.getvalue()
        csv_base64 = base64.b64encode(csv_content.encode()).decode()

        return {"base_64": csv_base64}

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

        outcome_transactions = [
            t for t in transactions if t.type == TransactionType.OUTCOME
        ]
        income_transactions = [
            t for t in transactions if t.type == TransactionType.INCOME
        ]

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
