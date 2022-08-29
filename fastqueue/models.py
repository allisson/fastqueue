import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = sqlalchemy.MetaData()

topics = sqlalchemy.Table(
    "topics",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String(length=128), primary_key=True, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
)

queues = sqlalchemy.Table(
    "queues",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String(length=128), primary_key=True, nullable=False),
    sqlalchemy.Column(
        "topic_id",
        sqlalchemy.String(length=128),
        sqlalchemy.ForeignKey("topics.id"),
        index=True,
        nullable=False,
    ),
    sqlalchemy.Column("ack_deadline_seconds", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("message_retention_seconds", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("message_filters", JSONB, nullable=True),
    sqlalchemy.Column("dead_letter_queue_name", sqlalchemy.String(length=128), nullable=True),
    sqlalchemy.Column("dead_letter_max_retries", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("dead_letter_min_backoff_seconds", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("dead_letter_max_backoff_seconds", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, nullable=False),
)

messages = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", UUID, primary_key=True, nullable=False),
    sqlalchemy.Column(
        "queue_id", sqlalchemy.String(length=128), sqlalchemy.ForeignKey("queues.id"), nullable=False
    ),
    sqlalchemy.Column("data", JSONB, nullable=False),
    sqlalchemy.Column("attributes", JSONB, nullable=True),
    sqlalchemy.Column("delivery_attempts", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("expired_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("scheduled_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Index("ix_messages_expired_at", "expired_at", postgresql_using="brin"),
    sqlalchemy.Index("ix_messages_scheduled_at", "scheduled_at", postgresql_using="brin"),
    sqlalchemy.Index(
        "ix_messages_expired_at_scheduled_at", "expired_at", "scheduled_at", postgresql_using="brin"
    ),
)
