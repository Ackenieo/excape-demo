"""add run messages and challenges tables

Revision ID: 20260516_0002
Revises: 20260516_0001
Create Date: 2026-05-16 00:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260516_0002"
down_revision = "20260516_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "run_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=True),
        sa.Column("shake_delta", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["game_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_messages_run_id"), "run_messages", ["run_id"], unique=False)

    op.create_table(
        "challenges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("target_level_id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("share_title", sa.String(length=255), nullable=True),
        sa.Column("creator_nickname", sa.String(length=64), nullable=True),
        sa.Column("source_score", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["game_runs.id"]),
        sa.ForeignKeyConstraint(["target_level_id"], ["levels.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_challenges_code"), "challenges", ["code"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_challenges_code"), table_name="challenges")
    op.drop_table("challenges")
    op.drop_index(op.f("ix_run_messages_run_id"), table_name="run_messages")
    op.drop_table("run_messages")
