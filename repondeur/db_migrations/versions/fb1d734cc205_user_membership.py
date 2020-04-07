"""User membership

Revision ID: fb1d734cc205
Revises: f4d9b3233d41
Create Date: 2020-04-07 11:30:57.329120

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fb1d734cc205"
down_revision = "f4d9b3233d41"
branch_labels = None
depends_on = None


def upgrade():
    chambre_type = postgresql.ENUM(
        "AN", "SENAT", "CCFP", "CSFPE", name="chambre", create_type=False
    )
    op.create_table(
        "users_chambres",
        sa.Column("user_pk", sa.Integer(), nullable=False),
        sa.Column("chambre", chambre_type, nullable=False,),
        sa.Column("organisation", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_pk"],
            ["users.pk"],
            name=op.f("users_chambres_user_pk_fkey"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_pk", "chambre"),
    )


def downgrade():
    op.drop_table("users_chambres")
