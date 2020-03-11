"""Add chambre constraint

Revision ID: 245e371cbf82
Revises: 95dfdcde1955
Create Date: 2020-03-11 17:52:02.715512

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "245e371cbf82"
down_revision = "95dfdcde1955"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        op.f("ck_conseils_chambre"), "conseils", "chambre NOT IN ('AN', 'SENAT')",
    )


def downgrade():
    op.drop_constraint(op.f("ck_conseils_chambre"), "conseils")
