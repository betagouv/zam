"""Remove articles revisions

Revision ID: bf01601790f4
Revises: 67d0e6748a64
Create Date: 2019-01-18 21:42:06.814079

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bf01601790f4"
down_revision = "67d0e6748a64"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("article_user_contents_revisions")


def downgrade():
    op.create_table(
        "article_user_contents_revisions",
        sa.Column("pk", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column("title", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("presentation", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("user_pk", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("article_pk", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("user_content_pk", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["article_pk"],
            ["articles.pk"],
            name="article_user_contents_revisions_article_pk_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_content_pk"],
            ["article_user_contents.pk"],
            name="article_user_contents_revisions_user_content_pk_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_pk"],
            ["users.pk"],
            name="article_user_contents_revisions_user_pk_fkey",
        ),
        sa.PrimaryKeyConstraint("pk", name="article_user_contents_revisions_pkey"),
    )
