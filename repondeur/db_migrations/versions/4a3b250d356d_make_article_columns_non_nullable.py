"""Make article columns non-nullable

Revision ID: 4a3b250d356d
Revises: 6756d255959a
Create Date: 2018-11-08 15:09:36.560536

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a3b250d356d"
down_revision = "6756d255959a"
branch_labels = None
depends_on = None


def upgrade():
    for col_name in ["type", "num", "mult", "pos"]:
        op.execute(f"UPDATE articles SET {col_name} = '' WHERE {col_name} IS NULL;")
        op.alter_column("articles", col_name, nullable=False)


def downgrade():
    for col_name in ["type", "num", "mult", "pos"]:
        op.alter_column("articles", col_name, nullable=True)
