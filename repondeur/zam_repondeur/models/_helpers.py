from typing import Any, Iterable

from sqlalchemy.dialects.postgresql import ENUM


def alter_pg_enum(
    op: Any,
    type_name: str,
    new_values: Iterable[str],
    columns_to_convert: Iterable[str],
) -> None:
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
