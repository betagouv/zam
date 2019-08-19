"""Table for a given lecture

Revision ID: d3b8033f60c4
Revises: c2b357257d2c
Create Date: 2019-02-06 11:55:25.364164

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d3b8033f60c4"
down_revision = "c2b357257d2c"
branch_labels = None
depends_on = None


def upgrade():
    # Remove existing user tables not associated to a any lecture.
    op.drop_constraint(
        "amendements_user_table_pk_fkey", "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "user_table_pk")
    op.drop_table("user_tables")
    op.create_table(
        "user_tables",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=False),
        sa.Column("lecture_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.ForeignKeyConstraint(["lecture_pk"], ["lectures.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.create_index(
        "ix_user_tables__lecture_pk", "user_tables", ["lecture_pk"], unique=False
    )
    op.create_index("ix_user_tables__user_pk", "user_tables", ["user_pk"], unique=False)
    op.create_unique_constraint(
        "user_tables_user_pk_lecture_pk_key", "user_tables", ["user_pk", "lecture_pk"]
    )
    op.add_column(
        "amendements", sa.Column("user_table_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "amendements_user_table_pk_fkey",
        "amendements",
        "user_tables",
        ["user_table_pk"],
        ["pk"],
    )


def downgrade():
    raise NotImplementedError
