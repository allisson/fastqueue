from datetime import datetime
from uuid import UUID

from pydantic import BaseModel as Schema
from pydantic import Field

from fastqueue.config import settings

regex_for_id = "^[a-zA-Z0-9-._]+$"


class CreateTopicSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)


class TopicSchema(Schema):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


class ListTopicSchema(Schema):
    data: list[TopicSchema]


class CreateQueueSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)
    topic_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int = Field(
        ..., ge=settings.min_ack_deadline_seconds, le=settings.max_ack_deadline_seconds
    )
    message_retention_seconds: int = Field(
        ..., ge=settings.min_message_retention_seconds, le=settings.max_message_retention_seconds
    )
    message_filters: dict[str, list[str]] | None = None
    message_max_deliveries: int | None = Field(
        None, ge=settings.min_message_max_deliveries, le=settings.max_message_max_deliveries
    )


class UpdateQueueSchema(Schema):
    topic_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int = Field(
        ..., ge=settings.min_ack_deadline_seconds, le=settings.max_ack_deadline_seconds
    )
    message_retention_seconds: int = Field(
        ..., ge=settings.min_message_retention_seconds, le=settings.max_message_retention_seconds
    )
    message_filters: dict[str, list[str]] | None = None
    message_max_deliveries: int | None = Field(
        None, ge=settings.min_message_max_deliveries, le=settings.max_message_max_deliveries
    )


class QueueSchema(Schema):
    id: str
    topic_id: str | None
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict[str, list[str]] | None
    message_max_deliveries: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ListQueueSchema(Schema):
    data: list[QueueSchema]


class CreateMessageSchema(Schema):
    data: dict
    attributes: dict | None = None


class MessageSchema(Schema):
    id: UUID
    queue_id: str
    data: dict
    attributes: dict | None = None
    delivery_attempts: int
    expired_at: datetime
    scheduled_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ListMessageSchema(Schema):
    data: list[MessageSchema]
