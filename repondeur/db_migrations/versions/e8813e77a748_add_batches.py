"""Add batches

Revision ID: e8813e77a748
Revises: 9414986ec796
Create Date: 2019-05-23 15:22:38.031250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8813e77a748"
down_revision = "9414986ec796"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "batches",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.add_column("amendements", sa.Column("batch_pk", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("amendements_batch_pk_fkey"),
        "amendements",
        "batches",
        ["batch_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        op.f("amendements_batch_pk_fkey"), "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "batch_pk")
    op.drop_table("batches")
