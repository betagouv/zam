"""Add email whitelist

Revision ID: d42c23832d27
Revises: a6ddcbf66d93
Create Date: 2019-09-03 09:14:33.962769

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d42c23832d27"
down_revision = "a6ddcbf66d93"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "allowed_email_patterns",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("pattern", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("pattern", name=op.f("allowed_email_patterns_pattern_key")),
    )


def downgrade():
    op.drop_table("allowed_email_patterns")
