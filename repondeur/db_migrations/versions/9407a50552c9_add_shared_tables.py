"""Add shared tables

Revision ID: 9407a50552c9
Revises: 851d659d6eef
Create Date: 2019-07-22 15:48:01.842154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9407a50552c9"
down_revision = "851d659d6eef"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "shared_tables",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("titre", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("lecture_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["lecture_pk"], ["lectures.pk"], name=op.f("shared_tables_lecture_pk_fkey")
        ),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("slug", name=op.f("shared_tables_slug_key")),
    )
    op.create_index(
        "ix_shared_tables__lecture_pk", "shared_tables", ["lecture_pk"], unique=False
    )
    op.add_column(
        "amendements", sa.Column("shared_table_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("amendements_shared_table_pk_fkey"),
        "amendements",
        "shared_tables",
        ["shared_table_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        op.f("amendements_shared_table_pk_fkey"), "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "shared_table_pk")
    op.drop_index("ix_shared_tables__lecture_pk", table_name="shared_tables")
    op.drop_table("shared_tables")
