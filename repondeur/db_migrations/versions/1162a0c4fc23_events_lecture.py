"""Refactor the lecture journal to use events (like articles and amendements)

Revision ID: 1162a0c4fc23
Revises: a90e77416ebe
Create Date: 2019-01-28 14:55:41.056170

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1162a0c4fc23"
down_revision = "a90e77416ebe"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("journal")
    op.add_column("events", sa.Column("lecture_pk", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "events_lecture_pk_fkey", "events", "lectures", ["lecture_pk"], ["pk"]
    )


def downgrade():
    op.drop_constraint("events_lecture_pk_fkey", "events", type_="foreignkey")
    op.drop_column("events", "lecture_pk")
    op.create_table(
        "journal",
        sa.Column("pk", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("kind", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("message", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("lecture_pk", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["lecture_pk"], ["lectures.pk"], name="journal_lecture_pk_fkey"
        ),
        sa.PrimaryKeyConstraint("pk", name="journal_pkey"),
    )
