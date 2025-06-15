"""create elements table

Revision ID: 8b98b63bddf0
Revises: c6319a69348b
Create Date: 2025-06-15 22:04:25.566296

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b98b63bddf0"
down_revision: Union[str, None] = "c6319a69348b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "links",
        sa.Column("element_id", sa.Integer, primary_key=True),
        sa.Column("content", sa.String, nullable=False),
        sa.Column(
            "creation_date", sa.Date, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expiration_date", sa.Date, nullable=False),
    )
    op.create_table(
        "elements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("element_type", sa.String(50), nullable=False),
        sa.Column(
            "element_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("links")
    op.drop_table("elements")
