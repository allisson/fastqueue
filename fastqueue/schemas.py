from datetime import datetime
from uuid import UUID

from pydantic import BaseModel as Schema
from pydantic import Field, root_validator

from fastqueue.config import settings

regex_for_id = "^[a-zA-Z0-9-._]+$"


class NotFoundSchema(Schema):
    detail: str


class CreateTopicSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)


class TopicSchema(Schema):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


class ListTopicSchema(Schema):
    data: list[TopicSchema]


def message_max_deliveries_is_required_for_dead_queue_id(values):
    dead_queue_id = values.get("dead_queue_id", None)
    message_max_deliveries = values.get("message_max_deliveries", None)

    if dead_queue_id is not None and message_max_deliveries is None:
        raise ValueError("message_max_deliveries is required for dead queue support")
    if dead_queue_id is None and message_max_deliveries is not None:
        raise ValueError("dead_queue_id is required for dead queue support")

    return values


class CreateQueueSchema(Schema):
    id: str = Field(..., regex=regex_for_id, max_length=128)
    topic_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    dead_queue_id: str | None = Field(None, regex=regex_for_id, max_length=128)
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

    @root_validator()
    def message_max_deliveries_is_required_for_dead_queue_id(cls, values):
        return message_max_deliveries_is_required_for_dead_queue_id(values)


class UpdateQueueSchema(Schema):
    topic_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    dead_queue_id: str | None = Field(None, regex=regex_for_id, max_length=128)
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

    @root_validator()
    def message_max_deliveries_is_required_for_dead_queue_id(cls, values):
        return message_max_deliveries_is_required_for_dead_queue_id(values)


class QueueSchema(Schema):
    id: str
    topic_id: str | None
    dead_queue_id: str | None
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict[str, list[str]] | None
    message_max_deliveries: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class QueueStatsSchema(Schema):
    num_undelivered_messages: int
    oldest_unacked_message_age_seconds: int


class ListQueueSchema(Schema):
    data: list[QueueSchema]


class CreateMessageSchema(Schema):
    data: dict
    attributes: dict[str, str] | None = None


class MessageSchema(Schema):
    id: UUID
    queue_id: str
    data: dict
    attributes: dict[str, str] | None = None
    delivery_attempts: int
    expired_at: datetime
    scheduled_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ListMessageSchema(Schema):
    data: list[MessageSchema]
