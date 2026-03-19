"""add meeting approving status

Revision ID: d4f7a9b2c311
Revises: 7acee253eabe
Create Date: 2026-03-19 16:10:00.000000

"""

# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4f7a9b2c311"
down_revision: str | None = "7acee253eabe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Insert APPROVING between CREATED(0) and ANNOUNCED(2)
    # by shifting persisted ANNOUNCED..CLOSED values +1.
    op.execute(sa.text("UPDATE meeting SET status = status + 1 WHERE status >= 1"))


def downgrade() -> None:
    # Collapse APPROVING back to CREATED for backward compatibility.
    op.execute(sa.text("UPDATE meeting SET status = 0 WHERE status = 1"))
    op.execute(sa.text("UPDATE meeting SET status = status - 1 WHERE status >= 2"))
