from datetime import datetime

from sqlalchemy.orm import Session

from fastqueue.exceptions import NotFoundError
from fastqueue.models import Queue, Topic
from fastqueue.schemas import (
    CreateQueueSchema,
    CreateTopicSchema,
    QueueSchema,
    TopicSchema,
    UpdateQueueSchema,
)


class TopicService:
    @classmethod
    def create(cls, data: CreateTopicSchema, session: Session) -> TopicSchema:
        topic = Topic(id=data.id, created_at=datetime.utcnow())
        session.add(topic)
        return TopicSchema(id=topic.id, created_at=topic.created_at)

    @classmethod
    def get(cls, id: str, session: Session) -> TopicSchema:
        topic = session.query(Topic).filter_by(id=id).first()
        if topic is None:
            raise NotFoundError("topic not found")
        return TopicSchema(id=topic.id, created_at=topic.created_at)

    @classmethod
    def delete(cls, id: str, session: Session) -> None:
        cls.get(id, session=session)
        session.query(Topic).filter_by(id=id).delete()


class QueueService:
    @classmethod
    def to_schema(cls, queue: Queue) -> QueueSchema:
        return QueueSchema(
            id=queue.id,
            topic_id=queue.topic_id,
            ack_deadline_seconds=queue.ack_deadline_seconds,
            message_retention_seconds=queue.message_retention_seconds,
            message_filters=queue.message_filters,
            dead_letter_max_retries=queue.dead_letter_max_retries,
            dead_letter_min_backoff_seconds=queue.dead_letter_min_backoff_seconds,
            dead_letter_max_backoff_seconds=queue.dead_letter_max_backoff_seconds,
            created_at=queue.created_at,
            updated_at=queue.updated_at,
        )

    @classmethod
    def create(cls, data: CreateQueueSchema, session: Session) -> QueueSchema:
        topic = TopicService.get(data.topic_id, session=session)
        now = datetime.utcnow()
        queue = Queue(
            id=data.id,
            topic_id=topic.id,
            ack_deadline_seconds=data.ack_deadline_seconds,
            message_retention_seconds=data.message_retention_seconds,
            message_filters=data.message_filters,
            dead_letter_max_retries=data.dead_letter_max_retries,
            dead_letter_min_backoff_seconds=data.dead_letter_min_backoff_seconds,
            dead_letter_max_backoff_seconds=data.dead_letter_max_backoff_seconds,
            created_at=now,
            updated_at=now,
        )
        session.add(queue)
        return cls.to_schema(queue)

    @classmethod
    def update(cls, id: str, data: UpdateQueueSchema, session: Session) -> QueueSchema:
        topic = TopicService.get(data.topic_id, session=session)
        queue = cls.get(id, session=session)
        queue.topic_id = topic.id
        queue.ack_deadline_seconds = data.ack_deadline_seconds
        queue.message_retention_seconds = data.message_retention_seconds
        queue.message_filters = data.message_filters
        queue.dead_letter_max_retries = data.dead_letter_max_retries
        queue.dead_letter_min_backoff_seconds = data.dead_letter_min_backoff_seconds
        queue.dead_letter_max_backoff_seconds = data.dead_letter_max_backoff_seconds
        queue.created_at = queue.created_at
        queue.updated_at = datetime.utcnow()
        return cls.to_schema(queue)

    @classmethod
    def get(cls, id: str, session: Session) -> QueueSchema:
        queue = session.query(Queue).filter_by(id=id).first()
        if queue is None:
            raise NotFoundError("queue not found")
        return cls.to_schema(queue)

    @classmethod
    def delete(cls, id: str, session: Session) -> None:
        cls.get(id, session=session)
        session.query(Queue).filter_by(id=id).delete()
