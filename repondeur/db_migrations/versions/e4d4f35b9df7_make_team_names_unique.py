"""Make team names unique

Revision ID: e4d4f35b9df7
Revises: b03b7f1042e3
Create Date: 2019-03-26 13:44:59.968760

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e4d4f35b9df7"
down_revision = "b03b7f1042e3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(op.f("teams_name_key"), "teams", ["name"])


def downgrade():
    op.drop_constraint(op.f("teams_name_key"), "teams", type_="unique")
