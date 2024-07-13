from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette import status

from app.deps import SessionDep, CurrentUser
from app.schemas import (
    TransactionExportCsv,
    TransactionImportCsv,
    TransactionPublic,
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionSummary,
    TransactionUpdate,
)
from app.service.transaction_service import TransactionService

router = APIRouter()


@router.post(
    "", tags=["transactions"], response_model=TransactionPublic, status_code=201
)
def create_transaction_endpoint(
    session: SessionDep, current_user: CurrentUser, transaction: TransactionCreate
):
    transaction_service = TransactionService(session)
    return transaction_service.create_transaction(transaction, current_user)


@router.patch(
    "", tags=["transactions"], response_model=TransactionPublic, status_code=200
)
def update_transaction_endpoint(
    session: SessionDep, current_user: CurrentUser, transaction: TransactionUpdate
):
    transaction_service = TransactionService(session)
    return transaction_service.update_transaction(transaction, current_user)


@router.post("/import-csv", tags=["transactions"], status_code=201)
def create_transactions_from_csv(
    session: SessionDep,
    current_user: CurrentUser,
    transaction_import_csv: TransactionImportCsv,
):
    transaction_service = TransactionService(session)
    transaction_service.create_transactions_from_csv(
        transaction_import_csv, current_user
    )


@router.get("", tags=["transactions"], response_model=List[TransactionPublic])
def get_transactions_endpoint(
    session: SessionDep, current_user: CurrentUser, year_month: str
):
    transaction_service = TransactionService(session)
    return transaction_service.get_transactions(year_month, current_user)


@router.get(
    "/transaction-months",
    tags=["transactions"],
    response_model=List[TransactionFormattedMonthsWithTransactions],
)
def get_months_with_transactions_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
):
    transaction_service = TransactionService(session)
    return transaction_service.get_months_with_transactions(current_user)


@router.get(
    "/summary",
    tags=["transactions"],
    response_model=TransactionSummary,
)
def get_transaction_summary_endpoint(
    session: SessionDep, current_user: CurrentUser, year_month: str
):
    transaction_service = TransactionService(session)
    return transaction_service.get_transaction_summary(year_month, current_user)


@router.get("/export-csv", tags=["transactions"], response_model=TransactionExportCsv)
def export_transactions_csv(
    session: SessionDep, current_user: CurrentUser, year_month: str
):
    transaction_service = TransactionService(session)
    return transaction_service.export_transactions_csv(year_month, current_user)


@router.delete(
    "/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["transactions"]
)
def delete_transaction_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
    transaction_id: int,
):
    transaction_service = TransactionService(session)
    transaction_service.delete_transaction(current_user, transaction_id)
