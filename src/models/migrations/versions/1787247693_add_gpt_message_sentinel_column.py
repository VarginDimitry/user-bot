"""add sa_orm_sentinel column to gpt_message

Revision ID: 1787247693
Revises: 1773284580
Create Date: 2026-09-18 17:40:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1787247693"
down_revision: Union[str, Sequence[str], None] = "1773284580"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TABLE gpt_message ADD COLUMN IF NOT EXISTS sa_orm_sentinel INTEGER"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("gpt_message", "sa_orm_sentinel")
