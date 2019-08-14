"""Add events for dossiers

Revision ID: 3801b54623bc
Revises: a4315badfc30
Create Date: 2019-07-11 13:40:22.351453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3801b54623bc"
down_revision = "a4315badfc30"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("events", sa.Column("dossier_pk", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("events_dossier_pk_fkey"), "events", "dossiers", ["dossier_pk"], ["pk"]
    )


def downgrade():
    op.drop_constraint(op.f("events_dossier_pk_fkey"), "events", type_="foreignkey")
    op.drop_column("events", "dossier_pk")
