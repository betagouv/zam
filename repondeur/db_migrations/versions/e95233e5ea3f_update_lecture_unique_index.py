"""Update lecture unique index

Revision ID: e95233e5ea3f
Revises: 58a93f6ba5d2
Create Date: 2019-05-28 15:53:46.470846

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e95233e5ea3f"
down_revision = "58a93f6ba5d2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_lectures__texte_pk__partie__organe",
        "lectures",
        ["texte_pk", "partie", "organe"],
        unique=True,
    )
    op.drop_index(
        "ix_lectures__chambre__session__partie__organe", table_name="lectures"
    )


def downgrade():
    op.create_index(
        "ix_lectures__chambre__session__partie__organe",
        "lectures",
        ["chambre", "session", "partie", "organe"],
        unique=True,
    )
    op.drop_index("ix_lectures__texte_pk__partie__organe", table_name="lectures")
