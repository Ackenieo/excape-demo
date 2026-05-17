"""add player profile fields

Revision ID: 20260516_0003
Revises: 20260516_0002
Create Date: 2026-05-16 10:35:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260516_0003"
down_revision = "20260516_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("players", sa.Column("avatar_url", sa.String(length=255), nullable=True))
    op.add_column(
        "players",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', NOW())"),
        ),
    )
    op.alter_column("players", "updated_at", server_default=None)


def downgrade():
    op.drop_column("players", "updated_at")
    op.drop_column("players", "avatar_url")
