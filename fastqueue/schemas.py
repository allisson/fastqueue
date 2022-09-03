from datetime import datetime
from uuid import UUID

from pydantic import BaseModel as Schema
from pydantic import Field

regex_for_id = "^[a-zA-Z0-9-._]+$"


class CreateTopicSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)


class TopicSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)
    created_at: datetime


class CreateQueueSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)
    topic_id: str = Field(..., regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict | None = None
    dead_letter_queue_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    dead_letter_max_retries: int | None = None
    dead_letter_min_backoff_seconds: int | None = None
    dead_letter_max_backoff_seconds: int | None = None


class UpdateQueueSchema(Schema):
    topic_id: str = Field(..., regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict | None = None
    dead_letter_queue_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    dead_letter_max_retries: int | None = None
    dead_letter_min_backoff_seconds: int | None = None
    dead_letter_max_backoff_seconds: int | None = None


class QueueSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)
    topic_id: str = Field(..., regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict | None = None
    dead_letter_queue_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    dead_letter_max_retries: int | None = None
    dead_letter_min_backoff_seconds: int | None = None
    dead_letter_max_backoff_seconds: int | None = None
    created_at: datetime
    updated_at: datetime


class CreateMessageSchema(Schema):
    data: dict
    attributes: dict | None = None


class MessageSchema(Schema):
    id: UUID
    queue_id: str = Field(..., regex=regex_for_id, max_length=128)
    data: dict
    attributes: dict | None = None
    delivery_attempts: int
    created_at: datetime
    updated_at: datetime
