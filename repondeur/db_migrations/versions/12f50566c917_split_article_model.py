"""Split Article model

Revision ID: 12f50566c917
Revises: cbb2e504c783
Create Date: 2018-12-10 11:31:28.275275

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "12f50566c917"
down_revision = "cbb2e504c783"
branch_labels = None
depends_on = None


def upgrade():
    article_user_contents = op.create_table(
        "article_user_contents",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("presentation", sa.Text(), nullable=True),
        sa.Column("article_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["article_pk"], ["articles.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )
    connection = op.get_bind()
    results = connection.execute("SELECT pk, titre, jaune FROM articles;")
    op.bulk_insert(
        article_user_contents,
        [
            {"article_pk": pk, "title": titre, "presentation": jaune}
            for pk, titre, jaune in results
        ],
    )
    op.drop_column("articles", "titre")
    op.drop_column("articles", "jaune")


def downgrade():
    raise NotImplementedError
