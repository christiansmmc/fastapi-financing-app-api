from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str


class TokenPayload(SQLModel):
    sub: str | None = None


class Login(SQLModel):
    email: str
    password: str


class UserCreate(SQLModel):
    email: str
    password: str


class UserPublic(SQLModel):
    id: int
    email: str


class TagPublic(SQLModel):
    id: int
    name: str


class TransactionType(str, Enum):
    OUTCOME = "OUTCOME"
    INCOME = "INCOME"


class TransactionCreate(SQLModel):
    name: str
    description: Optional[str] = None
    value: float
    transaction_date: Optional[date] = None
    type: Optional[TransactionType] = None
    tag_id: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.transaction_date is None:
            self.transaction_date = date.today()
        if self.type is None:
            self.type = TransactionType.OUTCOME


class TransactionUpdate(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    value: float
    transaction_date: date
    type: TransactionType
    tag_id: Optional[int] = None


class TransactionImportCsv(SQLModel):
    bank_name: str
    transactions_date: str
    csv_base64: str


class TransactionExportCsv(SQLModel):
    base_64: str


class TransactionPublic(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    value: float
    transaction_date: Optional[date] = None
    type: TransactionType
    tag: Optional[TagPublic] = None


class TransactionMonthsWithTransactions(SQLModel):
    year: int
    month: int


class TransactionFormattedMonthsWithTransactions(SQLModel):
    date: str
    formattedDate: str


class TransactionSummary(SQLModel):
    formattedDate: str
    initialDate: date
    lastDate: date
    totalOutcome: float
    totalIncome: float
    profit: float
