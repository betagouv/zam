"""Add articles user content revisions

Revision ID: a79e7aa5121e
Revises: 06e826937905
Create Date: 2019-01-14 18:22:21.295787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a79e7aa5121e"
down_revision = "06e826937905"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "article_user_contents_revisions",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("presentation", sa.Text(), nullable=True),
        sa.Column("user_pk", sa.Integer(), nullable=True),
        sa.Column("article_pk", sa.Integer(), nullable=True),
        sa.Column("user_content_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_pk"], ["articles.pk"]),
        sa.ForeignKeyConstraint(["user_content_pk"], ["article_user_contents.pk"]),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )


def downgrade():
    op.drop_table("article_user_contents_revisions")
