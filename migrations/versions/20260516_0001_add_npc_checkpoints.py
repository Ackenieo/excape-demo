"""add npc checkpoints to levels and game runs

Revision ID: 20260516_0001
Revises: 
Create Date: 2026-05-16 00:01:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20260516_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'levels',
        sa.Column(
            'npc_checkpoints',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        'levels',
        sa.Column(
            'pass_threshold',
            sa.Integer(),
            nullable=False,
            server_default='1',
        ),
    )
    op.add_column(
        'game_runs',
        sa.Column(
            'passed_checkpoint_ids',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        'game_runs',
        sa.Column(
            'passed_checkpoint_count',
            sa.Integer(),
            nullable=False,
            server_default='0',
        ),
    )

    op.get_bind().exec_driver_sql(
        """
        UPDATE levels
        SET npc_checkpoints = $$[
          {"id":"urgent_reason","title":"紧急性成立","description":"玩家说明进入目的很紧急，拖延会造成明显后果。","hintForNpc":"只有具体且合理的紧急理由才算满足。","weight":1},
          {"id":"specific_evidence","title":"证据具体可信","description":"玩家给出可验证的信息，例如快递单号、药品信息、住户信息。","hintForNpc":"空泛保证不算，具体细节才算满足。","weight":1},
          {"id":"cooperative_attitude","title":"态度配合可控","description":"玩家愿意登记、接受监督、快速办完离开，体现风险可控。","hintForNpc":"如果玩家表现出配合态度，可以视为满足。","weight":1}
        ]$$::jsonb,
            pass_threshold = 2
        WHERE npc_checkpoints = '[]'::jsonb
        """
    )

    op.alter_column('levels', 'npc_checkpoints', server_default=None)
    op.alter_column('levels', 'pass_threshold', server_default=None)
    op.alter_column('game_runs', 'passed_checkpoint_ids', server_default=None)
    op.alter_column('game_runs', 'passed_checkpoint_count', server_default=None)


def downgrade():
    op.drop_column('game_runs', 'passed_checkpoint_count')
    op.drop_column('game_runs', 'passed_checkpoint_ids')
    op.drop_column('levels', 'pass_threshold')
    op.drop_column('levels', 'npc_checkpoints')
