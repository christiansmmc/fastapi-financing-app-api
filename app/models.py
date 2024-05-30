from datetime import date
from enum import Enum
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: str
    transactions: List["Transaction"] = Relationship(back_populates="user")


class TransactionType(str, Enum):
    OUTCOME = "OUTCOME"
    INCOME = "INCOME"


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    value: float
    transaction_date: date = Field(default_factory=lambda: date.today())
    type: TransactionType

    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id")
    tag: Tag = Relationship(back_populates=None)

    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Users = Relationship(back_populates="transactions")
