"""add content_compact video_structure content_analysis to hotspots

Revision ID: 329e9c42a115
Revises: 2f8ec66299cd
Create Date: 2025-11-14 15:19:52.591985

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '329e9c42a115'
down_revision = '2f8ec66299cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 只添加新字段，不删除其他表
    # 注意：这些表（langgraph_checkpoints, projects, users等）可能不属于当前项目
    # 如果它们存在且有依赖关系，删除操作会失败
    op.add_column('hotspots', sa.Column('content_compact', sa.Text(), nullable=True))
    op.add_column('hotspots', sa.Column('video_structure', sa.JSON(), nullable=True))
    op.add_column('hotspots', sa.Column('content_analysis', sa.JSON(), nullable=True))


def downgrade() -> None:
    # 只删除添加的字段
    op.drop_column('hotspots', 'content_analysis')
    op.drop_column('hotspots', 'video_structure')
    op.drop_column('hotspots', 'content_compact')
