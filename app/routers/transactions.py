from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from app.deps import SessionDep, CurrentUser
from app.repository.tags import get_tag_by_id
from app.repository.transactions import (
    create_transaction,
    get_transactions_by_date_between,
    find_months_with_transactions,
    get_transaction_by_id,
    delete_transaction,
)
from app.schemas import (
    TransactionPublic,
    TransactionCreate,
    TransactionFormattedMonthsWithTransactions,
    TransactionSummary,
    TransactionType,
)
from app.utils.date_utils import get_first_late_date_from_year_month, get_formatted_date

router = APIRouter()


@router.post("/", tags=["transactions"], response_model=TransactionPublic)
def create_transaction_endpoint(
    session: SessionDep, current_user: CurrentUser, transaction: TransactionCreate
):
    print(transaction)
    if transaction.tag_id:
        get_tag_by_id(session, transaction.tag_id)

    return create_transaction(session, transaction, current_user.id)


@router.get("/", tags=["transactions"], response_model=List[TransactionPublic])
def get_transactions_endpoint(
    session: SessionDep, current_user: CurrentUser, year_month: str
):
    first_day_of_month, last_day_of_month = get_first_late_date_from_year_month(
        year_month
    )

    return get_transactions_by_date_between(
        session, current_user.id, first_day_of_month, last_day_of_month
    )


@router.get(
    "/transaction-months",
    tags=["transactions"],
    response_model=List[TransactionFormattedMonthsWithTransactions],
)
def get_months_with_transactions_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
):
    months_with_transactions = find_months_with_transactions(session, current_user.id)

    response = [
        TransactionFormattedMonthsWithTransactions(
            date=f"{date.year}-{date.month:02d}",
            formattedDate=get_formatted_date(f"{date.year}-{date.month:02d}"),
        )
        for date in months_with_transactions
    ]

    return response


@router.get(
    "/summary",
    tags=["transactions"],
    response_model=TransactionSummary,
)
def get_transaction_summary_endpoint(
    session: SessionDep, current_user: CurrentUser, year_month: str
):
    first_day_of_month, last_day_of_month = get_first_late_date_from_year_month(
        year_month
    )
    transactions = get_transactions_by_date_between(
        session, current_user.id, first_day_of_month, last_day_of_month
    )

    outcome_transactions = filter(
        lambda transaction: transaction.type == TransactionType.OUTCOME, transactions
    )
    income_transactions = filter(
        lambda transaction: transaction.type == TransactionType.INCOME, transactions
    )

    total_outcome = sum(transactions.value for transactions in outcome_transactions)
    total_income = sum(transactions.value for transactions in income_transactions)
    profit = total_income - total_outcome

    summary = TransactionSummary(
        formattedDate=get_formatted_date(year_month),
        initialDate=first_day_of_month,
        lastDate=last_day_of_month,
        totalOutcome=total_outcome,
        totalIncome=total_income,
        profit=profit,
    )

    return summary


@router.delete(
    "/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["transactions"]
)
def delete_transaction_endpoint(
    session: SessionDep,
    current_user: CurrentUser,
    transaction_id: int,
):
    transaction = get_transaction_by_id(session, transaction_id)

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found!")

    delete_transaction(session, transaction_id)
