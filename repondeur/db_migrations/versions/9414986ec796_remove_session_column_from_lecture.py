"""Remove session column from Lecture

Revision ID: 9414986ec796
Revises: e95233e5ea3f
Create Date: 2019-05-28 15:56:30.416747

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9414986ec796"
down_revision = "e95233e5ea3f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("lectures", "session")


def downgrade():
    op.add_column(
        "lectures", sa.Column("session", sa.TEXT(), autoincrement=False, nullable=True)
    )
    raise NotImplementedError(
        "Would need to reconstruct data from texte.session or texte.legislature"
    )
