"""add invoice model

Revision ID: f36dd852a51c
Revises: b37dc52e745e
Create Date: 2025-12-24 22:06:26.610088

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'f36dd852a51c'
down_revision: Union[str, Sequence[str], None] = 'b37dc52e745e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
