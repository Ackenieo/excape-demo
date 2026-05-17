"""add public_id to custom_npcs

Revision ID: 20260516_0006
Revises: 20260516_0005
Create Date: 2026-05-16 00:06:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260516_0006"
down_revision = "20260516_0005"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("custom_npcs", sa.Column("public_id", sa.String(length=32), nullable=True))
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                'npc_custom_'
                || TO_CHAR(COALESCE(created_at, TIMEZONE('utc', NOW())), 'YYYYMMDD')
                || '_'
                || LPAD(
                    ROW_NUMBER() OVER (
                        PARTITION BY TO_CHAR(COALESCE(created_at, TIMEZONE('utc', NOW())), 'YYYYMMDD')
                        ORDER BY created_at, id
                    )::text,
                    3,
                    '0'
                ) AS generated_public_id
            FROM custom_npcs
        )
        UPDATE custom_npcs AS target
        SET public_id = ranked.generated_public_id
        FROM ranked
        WHERE target.id = ranked.id
        """
    )
    op.alter_column("custom_npcs", "public_id", nullable=False)
    op.create_index("ix_custom_npcs_public_id", "custom_npcs", ["public_id"], unique=True)


def downgrade():
    op.drop_index("ix_custom_npcs_public_id", table_name="custom_npcs")
    op.drop_column("custom_npcs", "public_id")
