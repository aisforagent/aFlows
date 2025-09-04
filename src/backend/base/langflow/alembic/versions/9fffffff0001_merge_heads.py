"""
Merge multiple heads into a single linear history.

This migration merges the two diverging heads so Alembic can
upgrade to 'head' without ambiguity when running Langflow.

Revision ID: 9fffffff0001
Revises: 0882f9657f22, 4522eb831f5c
Create Date: 2025-09-03 08:15:00
"""

from alembic import op  # noqa: F401


# revision identifiers, used by Alembic.
revision = "9fffffff0001"
down_revision = ("0882f9657f22", "4522eb831f5c")
branch_labels = None
depends_on = None


def upgrade() -> None:  # noqa: D401
    """No-op merge migration."""
    pass


def downgrade() -> None:  # noqa: D401
    """No-op downgrade for merge migration."""
    pass


