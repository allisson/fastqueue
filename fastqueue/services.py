import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from fastqueue.exceptions import NotFoundError
from fastqueue.models import Message, Queue, Topic
from fastqueue.schemas import (
    CreateMessageSchema,
    CreateQueueSchema,
    CreateTopicSchema,
    ListMessageSchema,
    ListQueueSchema,
    ListTopicSchema,
    MessageSchema,
    QueueSchema,
    TopicSchema,
    UpdateMessageSchema,
    UpdateQueueSchema,
)


def apply_basic_filters(query: Any, filters: dict | None, offset: int | None, limit: int | None) -> Any:
    if filters is not None:
        query = query.filter_by(**filters)
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query


class TopicService:
    @classmethod
    def create(cls, data: CreateTopicSchema, session: Session) -> TopicSchema:
        topic = Topic(id=data.id, created_at=datetime.utcnow())
        session.add(topic)
        session.commit()
        return TopicSchema.from_orm(topic)

    @classmethod
    def get_model(cls, id: str, session: Session) -> Topic | None:
        return session.query(Topic).filter_by(id=id).first()

    @classmethod
    def get(cls, id: str, session: Session) -> TopicSchema:
        topic = cls.get_model(id=id, session=session)
        if topic is None:
            raise NotFoundError("topic not found")
        return TopicSchema.from_orm(topic)

    @classmethod
    def list(
        cls, filters: dict | None, offset: int | None, limit: int | None, session: Session
    ) -> ListTopicSchema:
        topics = session.query(Topic).order_by(Topic.id)
        topics = apply_basic_filters(topics, filters, offset, limit)
        return ListTopicSchema(data=[TopicSchema.from_orm(topic) for topic in topics.all()])

    @classmethod
    def delete(cls, id: str, session: Session) -> None:
        cls.get(id, session=session)
        session.query(Topic).filter_by(id=id).delete()
        session.commit()


class QueueService:
    @classmethod
    def create(cls, data: CreateQueueSchema, session: Session) -> QueueSchema:
        if data.topic_id is not None:
            TopicService.get(data.topic_id, session=session)

        now = datetime.utcnow()
        queue = Queue(
            id=data.id,
            topic_id=data.topic_id,
            ack_deadline_seconds=data.ack_deadline_seconds,
            message_retention_seconds=data.message_retention_seconds,
            message_filters=data.message_filters,
            message_max_deliveries=data.message_max_deliveries,
            created_at=now,
            updated_at=now,
        )
        session.add(queue)
        session.commit()
        return QueueSchema.from_orm(queue)

    @classmethod
    def update(cls, id: str, data: UpdateQueueSchema, session: Session) -> QueueSchema:
        if data.topic_id is not None:
            TopicService.get(data.topic_id, session=session)

        queue = cls.get_model(id, session=session)
        queue.topic_id = data.topic_id
        queue.ack_deadline_seconds = data.ack_deadline_seconds
        queue.message_retention_seconds = data.message_retention_seconds
        queue.message_filters = data.message_filters
        queue.message_max_deliveries = data.message_max_deliveries
        queue.created_at = queue.created_at
        queue.updated_at = datetime.utcnow()
        session.commit()
        return QueueSchema.from_orm(queue)

    @classmethod
    def get_model(cls, id: str, session: Session) -> Queue:
        return session.query(Queue).filter_by(id=id).first()

    @classmethod
    def get(cls, id: str, session: Session) -> QueueSchema:
        queue = cls.get_model(id=id, session=session)
        if queue is None:
            raise NotFoundError("queue not found")
        return QueueSchema.from_orm(queue)

    @classmethod
    def list(
        cls, filters: dict | None, offset: int | None, limit: int | None, session: Session
    ) -> ListQueueSchema:
        queues = session.query(Queue).order_by(Queue.id)
        queues = apply_basic_filters(queues, filters, offset, limit)
        return ListQueueSchema(data=[QueueSchema.from_orm(queue) for queue in queues.all()])

    @classmethod
    def delete(cls, id: str, session: Session) -> None:
        cls.get(id, session=session)
        session.query(Queue).filter_by(id=id).delete()
        session.commit()


class MessageService:
    @classmethod
    def _should_message_be_created_on_queue(
        cls, queue_filters: dict[str, list[Any]] | None, message_attributes: dict | None
    ) -> bool:
        if queue_filters is not None:
            if message_attributes is None:
                return False

            keys = set(queue_filters.keys()).intersection(set(message_attributes.keys()))
            if len(keys) != len(queue_filters.keys()):
                return False

            for key in keys:
                if message_attributes[key] not in queue_filters[key]:
                    return False

        return True

    @classmethod
    def create(cls, topic_id: str, data: CreateMessageSchema, session: Session) -> ListMessageSchema:
        result = ListMessageSchema(data=[], offset=None, limit=None)
        topic = TopicService.get(topic_id, session=session)
        queues = QueueService.list(filters={"topic_id": topic.id}, offset=None, limit=None, session=session)
        if not queues.data:
            return result

        for queue in queues.data:
            if cls._should_message_be_created_on_queue(queue.message_filters, data.attributes) is False:
                continue

            now = datetime.utcnow()
            message = Message(
                id=uuid.uuid4().hex,
                queue_id=queue.id,
                data=data.data,
                attributes=data.attributes,
                delivery_attempts=0,
                expired_at=now + timedelta(seconds=queue.message_retention_seconds),
                scheduled_at=now,
                created_at=now,
                updated_at=now,
            )
            session.add(message)
            result.data.append(MessageSchema.from_orm(message))

        session.commit()
        return result

    @classmethod
    def update(cls, id: str, data: UpdateMessageSchema, session: Session) -> MessageSchema:
        message = cls.get_model(id, session=session)
        message.delivery_attempts = data.delivery_attempts
        message.scheduled_at = data.scheduled_at
        message.updated_at = datetime.utcnow()
        session.commit()
        return MessageSchema.from_orm(message)

    @classmethod
    def get_model(cls, id: str, session: Session) -> Message:
        return session.query(Message).filter_by(id=id).first()

    @classmethod
    def get(cls, id: str, session: Session) -> MessageSchema:
        message = cls.get_model(id=id, session=session)
        if message is None:
            raise NotFoundError("message not found")
        return MessageSchema.from_orm(message)

    @classmethod
    def list(
        cls, filters: dict | None, offset: int | None, limit: int | None, session: Session
    ) -> ListMessageSchema:
        messages = session.query(Message).order_by(Message.created_at)
        messages = apply_basic_filters(messages, filters, offset, limit)
        return ListMessageSchema(data=[MessageSchema.from_orm(message) for message in messages.all()])

    @classmethod
    def list_for_consume(cls, queue_id: str, limit: int, session: Session) -> ListMessageSchema:
        queue = QueueService.get(id=queue_id, session=session)
        now = datetime.utcnow()
        filters = [Message.queue_id == queue.id, Message.expired_at >= now, Message.scheduled_at <= now]
        if queue.message_max_deliveries is not None:
            filters.append(Message.delivery_attempts < queue.message_max_deliveries)

        data = []
        messages = (
            session.query(Message).filter(*filters).with_for_update(skip_locked=True).limit(limit).all()
        )
        for message in messages:
            message.delivery_attempts += 1
            message.scheduled_at = now + timedelta(seconds=queue.ack_deadline_seconds)
            message.updated_at = now
            data.append(MessageSchema.from_orm(message))

        session.commit()
        return ListMessageSchema(data=data)
