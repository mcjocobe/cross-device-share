"""create user table

Revision ID: c6319a69348b
Revises:
Create Date: 2025-05-23 23:42:24.053969

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import os

# revision identifiers, used by Alembic.
revision: str = "c6319a69348b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(f"CREATE USER admin WITH PASSWORD '{os.getenv("admin_pass")}';")

    op.execute("GRANT CONNECT ON DATABASE device_sharing TO admin;")
    op.execute("GRANT USAGE ON SCHEMA public TO admin;")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO admin;"
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
