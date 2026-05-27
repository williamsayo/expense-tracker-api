"""add soft delete field

Revision ID: ad2964c96b65
Revises: 0a63a0695062
Create Date: 2026-05-27 12:12:44.187812

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ad2964c96b65"
down_revision: Union[str, Sequence[str], None] = "0a63a0695062"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("discarded", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "discarded")
