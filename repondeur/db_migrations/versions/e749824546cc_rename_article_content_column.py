"""Rename article content column

Revision ID: e749824546cc
Revises: 12f50566c917
Create Date: 2018-12-10 11:47:10.351827

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e749824546cc"
down_revision = "12f50566c917"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("articles", "contenu", new_column_name="content")


def downgrade():
    op.alter_column("articles", "content", new_column_name="contenu")
