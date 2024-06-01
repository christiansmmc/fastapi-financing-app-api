from typing import List

from fastapi import APIRouter
from starlette import status

from app.deps import SessionDep, CurrentUser
from app.schemas import (
    TransactionPublic,
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionSummary,
)
from app.service.transaction_service import TransactionService

router = APIRouter()


@router.post("", tags=["transactions"], response_model=TransactionPublic)
def create_transaction_endpoint(
    session: SessionDep, current_user: CurrentUser, transaction: TransactionCreate
):
    transaction_service = TransactionService(session)
    return transaction_service.create_transaction(transaction, current_user)


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
