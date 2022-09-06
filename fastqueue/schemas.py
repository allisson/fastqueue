from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel as Schema
from pydantic import Field

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
    ack_deadline_seconds: int = Field(30, ge=0, le=600)
    message_retention_seconds: int = Field(1209600, ge=600, le=1209600)
    message_filters: dict[str, list[Any]] | None = None
    message_max_deliveries: int | None = Field(None, ge=1, le=1000)


class UpdateQueueSchema(Schema):
    topic_id: str | None = Field(None, regex=regex_for_id, max_length=128)
    ack_deadline_seconds: int = Field(..., ge=0, le=600)
    message_retention_seconds: int = Field(..., ge=600, le=1209600)
    message_filters: dict[str, list[Any]] | None = None
    message_max_deliveries: int | None = Field(None, ge=1, le=1000)


class QueueSchema(Schema):
    id: str
    topic_id: str | None
    ack_deadline_seconds: int
    message_retention_seconds: int
    message_filters: dict[str, list[Any]] | None
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


class UpdateMessageSchema(Schema):
    delivery_attempts: int
    scheduled_at: datetime


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
