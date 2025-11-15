"""Add heat_growth_rate to hotspots

Revision ID: 2f8ec66299cd
Revises: 8bfd37a0a132
Create Date: 2025-11-12 21:57:11.094145

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2f8ec66299cd'
down_revision = '8bfd37a0a132'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 只添加heat_growth_rate字段
    op.add_column('hotspots', sa.Column('heat_growth_rate', sa.Float(), nullable=True))


def downgrade() -> None:
    # 只删除heat_growth_rate字段
    op.drop_column('hotspots', 'heat_growth_rate')
