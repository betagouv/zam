"""Remove modified_at

Revision ID: 4455b60c7178
Revises: 72b5668e320f
Create Date: 2019-04-30 10:37:44.322768

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4455b60c7178"
down_revision = "72b5668e320f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("amendements", "modified_at")
    op.drop_column("articles", "modified_at")
    op.drop_column("lectures", "modified_at")


def downgrade():
    raise NotImplementedError
