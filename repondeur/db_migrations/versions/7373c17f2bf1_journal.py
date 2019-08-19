"""Journal

Revision ID: 7373c17f2bf1
Revises: a3962c18da56
Create Date: 2018-08-20 15:47:27.197244

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7373c17f2bf1"
down_revision = "a3962c18da56"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "journal",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("lecture_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["lecture_pk"], ["lectures.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )


def downgrade():
    op.drop_table("journal")
