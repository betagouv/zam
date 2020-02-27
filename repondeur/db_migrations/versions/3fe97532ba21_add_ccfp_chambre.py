"""Add CCFP chambre

Revision ID: 3fe97532ba21
Revises: f2882be74177
Create Date: 2020-02-27 14:25:49.524626

"""
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = "3fe97532ba21"
down_revision = "f2882be74177"
branch_labels = None
depends_on = None


COLUMNS_TO_CONVERT = [("lectures", "chambre"), ("textes", "chambre")]


def upgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT", "CCFP"], COLUMNS_TO_CONVERT)


def downgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT"], COLUMNS_TO_CONVERT)


def alter_pg_enum(op, type_name, new_values, columns_to_convert):
    """
    This is a safe way to add, rename or remove value to a Postgres Enum type.

    Note: if there are any indexes or constraints referencing the existing columns,
    you may need to remove them before, and add them again after.

    References:
    - https://blog.yo1.dog/updating-enum-values-in-postgresql-the-safe-and-easy-way/

    """

    # Rename old Enum type
    tmp_type_name = type_name + "_old"
    op.execute(f"ALTER TYPE {type_name} RENAME TO {tmp_type_name}")

    # Create new Enum type
    new_type = ENUM(*new_values, name=type_name)
    new_type.create(op.get_bind())

    # Convert existing columns to use the new Enum type
    for table_name, column_name in columns_to_convert:
        op.alter_column(
            table_name,
            column_name,
            type_=new_type,
            postgresql_using=f"{column_name}::text::{type_name}",
        )

    # Drop the old Enum type
    op.execute(f"DROP TYPE {tmp_type_name}")
