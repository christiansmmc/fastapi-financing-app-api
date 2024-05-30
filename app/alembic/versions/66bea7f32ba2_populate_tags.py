"""populate tags

Revision ID: 66bea7f32ba2
Revises: 28fca1cc4b1d
Create Date: 2024-05-29 13:22:21.812299

"""

import csv
import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "66bea7f32ba2"
down_revision: Union[str, None] = "28fca1cc4b1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Path to the CSV file
    csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "tag.csv")

    # Open the CSV file and read the data
    with open(csv_file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        rows = [row for row in reader]

    # Insert the data into the tag table
    op.bulk_insert(
        sa.Table(
            "tag",
            sa.MetaData(),
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String, nullable=False),
        ),
        rows,
    )


def downgrade() -> None:
    # Optionally, write a downgrade script to remove the inserted data
    pass
