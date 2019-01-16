"""Add events

Revision ID: 67d0e6748a64
Revises: a79e7aa5121e
Create Date: 2019-01-15 14:57:08.162415

"""
from alembic import op
from sqlalchemy_utils import JSONType, UUIDType
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "67d0e6748a64"
down_revision = "a79e7aa5121e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "events",
        sa.Column("pk", UUIDType(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=True),
        sa.Column("data", JSONType(), nullable=True),
        sa.Column("meta", JSONType(), nullable=True),
        sa.Column("article_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["article_pk"], ["articles.pk"]),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )


def downgrade():
    op.drop_table("events")
