"""Indexes on foreign keys to speed up lecture deletions

Revision ID: a6ddcbf66d93
Revises: aa4e290e0df2
Create Date: 2019-08-29 16:16:55.621907

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a6ddcbf66d93"
down_revision = "aa4e290e0df2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_amendement_user_contents__amendement_pk",
        "amendement_user_contents",
        ["amendement_pk"],
        unique=False,
    )
    op.create_index(
        "ix_amendements__parent_pk", "amendements", ["parent_pk"], unique=False
    )
    op.create_index(
        "ix_events__amendement_pk", "events", ["amendement_pk"], unique=False
    )


def downgrade():
    op.drop_index("ix_events__amendement_pk", table_name="events")
    op.drop_index("ix_amendements__parent_pk", table_name="amendements")
    op.drop_index(
        "ix_amendement_user_contents__amendement_pk",
        table_name="amendement_user_contents",
    )
