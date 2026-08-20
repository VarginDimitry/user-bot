"""add gpt_message

Revision ID: 1773284580
Revises: 17631877753
Create Date: 2026-08-09 20:03:00.000000

"""

from typing import Sequence, Union

import advanced_alchemy
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1773284580"
down_revision: Union[str, Sequence[str], None] = "17631877753"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "gpt_message",
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(), nullable=False),
        sa.Column("source_message_id", sa.String(), nullable=False),
        sa.Column("dialog_id", sa.String(), nullable=False),
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column(
            "created_at",
            advanced_alchemy.types.datetime.DateTimeUTC(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            advanced_alchemy.types.datetime.DateTimeUTC(timezone=True),
            nullable=False,
        ),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_gpt_message")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("gpt_message")
