import os

from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel

import app.models
import app.schemas

load_dotenv()

LOG_QUERIES = False

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=LOG_QUERIES)


def create_all_tables():
    SQLModel.metadata.create_all(engine)
