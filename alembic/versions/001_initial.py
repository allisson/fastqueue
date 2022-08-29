"""Auto generated

Revision ID: 4485cf5c36b9
Revises:
Create Date: 2022-08-29 18:44:21.413531

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "4485cf5c36b9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "topics",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "queues",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("topic_id", sa.String(length=128), nullable=False),
        sa.Column("ack_deadline_seconds", sa.Integer(), nullable=False),
        sa.Column("message_retention_seconds", sa.Integer(), nullable=False),
        sa.Column("message_filters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("dead_letter_queue_name", sa.String(length=128), nullable=True),
        sa.Column("dead_letter_max_retries", sa.Integer(), nullable=True),
        sa.Column("dead_letter_min_backoff_seconds", sa.Integer(), nullable=True),
        sa.Column("dead_letter_max_backoff_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_queues_topic_id"), "queues", ["topic_id"], unique=False)
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(), nullable=False),
        sa.Column("queue_id", sa.String(length=128), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("delivery_attempts", sa.Integer(), nullable=False),
        sa.Column("expired_at", sa.DateTime(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["queue_id"],
            ["queues.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_messages_expired_at", "messages", ["expired_at"], unique=False, postgresql_using="brin"
    )
    op.create_index(
        "ix_messages_expired_at_scheduled_at",
        "messages",
        ["expired_at", "scheduled_at"],
        unique=False,
        postgresql_using="brin",
    )
    op.create_index(
        "ix_messages_scheduled_at", "messages", ["scheduled_at"], unique=False, postgresql_using="brin"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_messages_scheduled_at", table_name="messages", postgresql_using="brin")
    op.drop_index("ix_messages_expired_at_scheduled_at", table_name="messages", postgresql_using="brin")
    op.drop_index("ix_messages_expired_at", table_name="messages", postgresql_using="brin")
    op.drop_table("messages")
    op.drop_index(op.f("ix_queues_topic_id"), table_name="queues")
    op.drop_table("queues")
    op.drop_table("topics")
    # ### end Alembic commands ###
