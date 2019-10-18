"""Split amendement locations

Revision ID: c07109c338b1
Revises: 7f4601bc696a
Create Date: 2019-10-18 09:58:06.174960

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c07109c338b1"
down_revision = "7f4601bc696a"
branch_labels = None
depends_on = None


def upgrade():
    amendement_location = op.create_table(
        "amendement_location",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("amendement_pk", sa.Integer(), nullable=False),
        sa.Column("user_table_pk", sa.Integer(), nullable=True),
        sa.Column("shared_table_pk", sa.Integer(), nullable=True),
        sa.Column("batch_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["amendement_pk"],
            ["amendements.pk"],
            name=op.f("amendement_location_amendement_pk_fkey"),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["batch_pk"], ["batches.pk"], name=op.f("amendement_location_batch_pk_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["shared_table_pk"],
            ["shared_tables.pk"],
            name=op.f("amendement_location_shared_table_pk_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["user_table_pk"],
            ["user_tables.pk"],
            name=op.f("amendement_location_user_table_pk_fkey"),
        ),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.create_index(
        "ix_amendement_location__amendement_pk",
        "amendement_location",
        ["amendement_pk"],
        unique=True,
    )

    # Migrate data
    connection = op.get_bind()
    amendements = connection.execute(
        "SELECT pk, user_table_pk, shared_table_pk, batch_pk FROM amendements;"
    )
    op.bulk_insert(
        amendement_location,
        [
            {
                "amendement_pk": pk,
                "user_table_pk": user_table_pk,
                "shared_table_pk": shared_table_pk,
                "batch_pk": batch_pk,
            }
            for pk, user_table_pk, shared_table_pk, batch_pk in amendements
        ],
    )

    op.drop_index(
        "ix_amendement_user_contents__amendement_pk",
        table_name="amendement_user_contents",
    )
    op.create_index(
        "ix_amendement_user_contents__amendement_pk",
        "amendement_user_contents",
        ["amendement_pk"],
        unique=True,
    )
    op.drop_constraint("amendements_batch_pk_fkey", "amendements", type_="foreignkey")
    op.drop_constraint(
        "amendements_shared_table_pk_fkey", "amendements", type_="foreignkey"
    )
    op.drop_constraint(
        "amendements_user_table_pk_fkey", "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "shared_table_pk")
    op.drop_column("amendements", "user_table_pk")
    op.drop_column("amendements", "batch_pk")


def downgrade():
    op.add_column(
        "amendements",
        sa.Column("batch_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "amendements",
        sa.Column("user_table_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "amendements",
        sa.Column("shared_table_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "amendements_user_table_pk_fkey",
        "amendements",
        "user_tables",
        ["user_table_pk"],
        ["pk"],
    )
    op.create_foreign_key(
        "amendements_shared_table_pk_fkey",
        "amendements",
        "shared_tables",
        ["shared_table_pk"],
        ["pk"],
    )
    op.create_foreign_key(
        "amendements_batch_pk_fkey", "amendements", "batches", ["batch_pk"], ["pk"]
    )
    op.drop_index(
        "ix_amendement_user_contents__amendement_pk",
        table_name="amendement_user_contents",
    )
    op.create_index(
        "ix_amendement_user_contents__amendement_pk",
        "amendement_user_contents",
        ["amendement_pk"],
        unique=False,
    )
    op.drop_index(
        "ix_amendement_location__amendement_pk", table_name="amendement_location"
    )

    # Migrate data
    connection = op.get_bind()
    amendement_locations = connection.execute(
        """
        SELECT amendement_pk, user_table_pk, shared_table_pk, batch_pk
        FROM amendement_location;
        """
    )
    for amendement_pk, user_table_pk, shared_table_pk, batch_pk in amendement_locations:
        op.execute(
            f"""
            UPDATE amendements
            SET
                user_table_pk = {user_table_pk or "null"},
                shared_table_pk = {shared_table_pk or "null"},
                batch_pk = {batch_pk or "null"}
            WHERE pk = {amendement_pk};
            """
        )

    op.drop_table("amendement_location")
