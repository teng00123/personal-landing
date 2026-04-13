"""add mfa fields to users

Revision ID: a1b2c3d4e5f6
Revises: bcc714072d0a
Create Date: 2026-04-13 09:55:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '7356bc3a04af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('mfa_secret', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('mfa_pending_secret', sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'mfa_pending_secret')
    op.drop_column('users', 'mfa_secret')
    op.drop_column('users', 'mfa_enabled')
