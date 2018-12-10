"""Rename Amendement contents columns

Revision ID: ccc17664477b
Revises: 181f05f634f4
Create Date: 2018-12-10 14:28:52.553077

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ccc17664477b"
down_revision = "181f05f634f4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("amendements", "objet", new_column_name="expose")
    op.alter_column("amendements", "dispositif", new_column_name="corps")


def downgrade():
    op.alter_column("amendements", "expose", new_column_name="objet")
    op.alter_column("amendements", "corps", new_column_name="dispositif")
