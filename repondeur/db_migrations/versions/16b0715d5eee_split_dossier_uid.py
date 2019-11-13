"""Split dossier uid

Revision ID: 16b0715d5eee
Revises: c07109c338b1
Create Date: 2019-11-06 17:26:15.327535

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "16b0715d5eee"
down_revision = "c07109c338b1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dossiers", sa.Column("an_id", sa.Text(), nullable=True))
    op.add_column("dossiers", sa.Column("senat_id", sa.Text(), nullable=True))
    op.create_unique_constraint(op.f("dossiers_an_id_key"), "dossiers", ["an_id"])
    op.create_unique_constraint(op.f("dossiers_senat_id_key"), "dossiers", ["senat_id"])
    op.execute(
        """
        UPDATE dossiers SET an_id = uid WHERE uid LIKE 'DL%';
        UPDATE dossiers SET senat_id = uid WHERE uid NOT LIKE 'DL%';
        """
    )
    op.create_check_constraint(
        op.f("ck_dossiers_an_id_senat_id"),
        "dossiers",
        "an_id IS NOT NULL OR senat_id IS NOT NULL",
    )
    op.drop_constraint("dossiers_uid_key", "dossiers", type_="unique")
    op.drop_column("dossiers", "uid")


def downgrade():
    op.add_column(
        "dossiers", sa.Column("uid", sa.TEXT(), autoincrement=False, nullable=False)
    )
    op.create_unique_constraint("dossiers_uid_key", "dossiers", ["uid"])
    op.drop_constraint(op.f("dossiers_senat_id_key"), "dossiers", type_="unique")
    op.drop_constraint(op.f("dossiers_an_id_key"), "dossiers", type_="unique")
    op.drop_constraint(op.f("ck_dossiers_an_id_senat_id"), "dossiers")
    op.drop_column("dossiers", "senat_id")
    op.drop_column("dossiers", "an_id")
