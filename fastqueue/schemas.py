from datetime import datetime
from uuid import UUID

from pydantic import BaseModel as Schema
from pydantic import Field, validator

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


def message_max_deliveries_is_required_for_dead_queue_id(v, values, **kwargs):
    if v is None:
        return v

    if values.get("message_max_deliveries", None) is None:
        raise ValueError("message_max_deliveries is required")

    return v


def dead_queue_id_is_required_for_message_max_deliveries(v, values, **kwargs):
    if v is None:
        return v

    if values.get("dead_queue_id", None) is None:
        raise ValueError("dead_queue_id is required")

    return v


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

    @validator("dead_queue_id")
    def message_max_deliveries_is_required_for_dead_queue_id(cls, v, values, **kwargs):
        return message_max_deliveries_is_required_for_dead_queue_id(v, values, **kwargs)

    @validator("message_max_deliveries")
    def dead_queue_id_is_required_for_message_max_deliveries(cls, v, values, **kwargs):
        return dead_queue_id_is_required_for_message_max_deliveries(v, values, **kwargs)


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

    @validator("dead_queue_id")
    def message_max_deliveries_is_required_for_dead_queue_id(cls, v, values, **kwargs):
        return message_max_deliveries_is_required_for_dead_queue_id(v, values, **kwargs)

    @validator("message_max_deliveries")
    def dead_queue_id_is_required_for_message_max_deliveries(cls, v, values, **kwargs):
        return dead_queue_id_is_required_for_message_max_deliveries(v, values, **kwargs)


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
