"""Make user content foreign keys non-nullable

Revision ID: 58a93f6ba5d2
Revises: 4455b60c7178
Create Date: 2019-05-10 13:58:08.339752

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "58a93f6ba5d2"
down_revision = "4455b60c7178"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM amendement_user_contents WHERE amendement_pk IS NULL;")
    op.alter_column(
        "amendement_user_contents",
        "amendement_pk",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.execute("DELETE FROM article_user_contents WHERE article_pk IS NULL;")
    op.alter_column(
        "article_user_contents",
        "article_pk",
        existing_type=sa.INTEGER(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "article_user_contents", "article_pk", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "amendement_user_contents",
        "amendement_pk",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
