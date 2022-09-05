import sqlalchemy
from sqlalchemy.dialects import postgresql

from fastqueue.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = sqlalchemy.Column(sqlalchemy.String(length=128), primary_key=True, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __repr__(self):
        return f"User(id={self.id!r})"


class Queue(Base):
    __tablename__ = "queues"

    id = sqlalchemy.Column(sqlalchemy.String(length=128), primary_key=True, nullable=False)
    topic_id = sqlalchemy.Column(
        sqlalchemy.String(length=128), sqlalchemy.ForeignKey("topics.id"), index=True, nullable=True
    )
    ack_deadline_seconds = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    message_retention_seconds = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    message_filters = sqlalchemy.Column(postgresql.JSONB, nullable=True)
    dead_letter_max_retries = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dead_letter_min_backoff_seconds = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dead_letter_max_backoff_seconds = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __repr__(self):
        return f"Queue(id={self.id!r}, topic_id={self.topic_id!r})"


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        sqlalchemy.Index("ix_messages_expired_at", "expired_at", postgresql_using="brin"),
        sqlalchemy.Index("ix_messages_scheduled_at", "scheduled_at", postgresql_using="brin"),
        sqlalchemy.Index(
            "ix_messages_expired_at_scheduled_at", "expired_at", "scheduled_at", postgresql_using="brin"
        ),
    )

    id = sqlalchemy.Column(postgresql.UUID, primary_key=True, nullable=False)
    queue_id = sqlalchemy.Column(
        sqlalchemy.String(length=128), sqlalchemy.ForeignKey("queues.id"), nullable=False
    )
    data = sqlalchemy.Column(postgresql.JSONB, nullable=False)
    attributes = sqlalchemy.Column(postgresql.JSONB, nullable=True)
    delivery_attempts = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    expired_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    scheduled_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    acked = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    dead = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __repr__(self):
        return f"Message(id={self.id!r}, queue_id={self.queue_id!r})"
