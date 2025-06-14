"""add user role

Revision ID: 2d994da7efc9
Revises: ced3a3ed742b
Create Date: 2025-06-08 17:13:28.595793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d994da7efc9'
down_revision: Union[str, None] = 'ced3a3ed742b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = sa.Enum('USER', 'ADMIN', name='userrole')


def upgrade() -> None:
    """Upgrade schema."""
    user_role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', user_role_enum, server_default='USER', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
