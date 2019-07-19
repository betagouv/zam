"""Change team dossier relation

Revision ID: 9022d8bc8ab9
Revises: c1b9e0409596
Create Date: 2019-07-19 16:40:38.352089

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9022d8bc8ab9"
down_revision = "c1b9e0409596"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("dossiers_owned_by_team_pk_fkey", "dossiers", type_="foreignkey")
    op.drop_column("dossiers", "owned_by_team_pk")
    op.drop_column("dossiers", "activated_at")
    op.add_column("teams", sa.Column("dossier_pk", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("teams_dossier_pk_fkey"), "teams", "dossiers", ["dossier_pk"], ["pk"]
    )


def downgrade():
    op.drop_constraint(op.f("teams_dossier_pk_fkey"), "teams", type_="foreignkey")
    op.drop_column("teams", "dossier_pk")
    op.add_column(
        "dossiers",
        sa.Column(
            "activated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "dossiers",
        sa.Column("owned_by_team_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "dossiers_owned_by_team_pk_fkey",
        "dossiers",
        "teams",
        ["owned_by_team_pk"],
        ["pk"],
    )
