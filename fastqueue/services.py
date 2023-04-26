import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastqueue.exceptions import AlreadyExistsError, NotFoundError
from fastqueue.models import Message, Queue, Topic
from fastqueue.schemas import (
    CreateMessageSchema,
    CreateQueueSchema,
    CreateTopicSchema,
    HealthSchema,
    ListMessageSchema,
    ListQueueSchema,
    ListTopicSchema,
    MessageSchema,
    QueueSchema,
    QueueStatsSchema,
    RedriveQueueSchema,
    TopicSchema,
    UpdateQueueSchema,
)


def apply_basic_filters(
    query: Any, filters: dict | None, offset: int | None, limit: int | None, order_by: Any | None = None
) -> Any:
    if filters is not None:
        query = query.filter_by(**filters)
    if order_by is not None:
        query = query.order_by(order_by)
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query


def list_model(
    model: Any,
    filters: dict | None,
    offset: int | None,
    limit: int | None,
    order_by: Any | None,
    session: Session,
) -> Any:
    query = session.query(model)
    query = apply_basic_filters(query=query, filters=filters, offset=offset, limit=limit, order_by=order_by)
    return query.all()


def get_model(model: Any, filters: dict | None, session: Session) -> Any:
    query = session.query(model)
    query = apply_basic_filters(query=query, filters=filters, offset=None, limit=None)
    instance = query.first()
    if instance is None:
        raise NotFoundError(f"{model.__name__} not found")
    return instance


def get_filters_for_consume(queue: Any, now: datetime) -> list:
    filters = [Message.queue_id == queue.id, Message.expired_at >= now, Message.scheduled_at <= now]
    if queue.dead_queue_id is not None and queue.message_max_deliveries is not None:
        filters.append(Message.delivery_attempts < queue.message_max_deliveries)
    return filters


class Service:
    def __init__(self, session: Session):
        self.session = session


class TopicService(Service):
    def create(self, data: CreateTopicSchema) -> TopicSchema:
        topic = Topic(id=data.id, created_at=datetime.utcnow())
        self.session.add(topic)
        try:
            self.session.commit()
        except IntegrityError:
            raise AlreadyExistsError("This topic already exists")
        return TopicSchema.from_orm(topic)

    def get(self, id: str) -> TopicSchema:
        topic = get_model(model=Topic, filters={"id": id}, session=self.session)
        return TopicSchema.from_orm(topic)

    def list(self, filters: dict | None, offset: int | None, limit: int | None) -> ListTopicSchema:
        topics = list_model(
            model=Topic, filters=filters, offset=offset, limit=limit, order_by=Topic.id, session=self.session
        )
        return ListTopicSchema(data=[TopicSchema.from_orm(topic) for topic in topics])

    def delete(self, id: str) -> None:
        topic = get_model(model=Topic, filters={"id": id}, session=self.session)
        self.session.query(Topic).filter_by(id=topic.id).delete()
        self.session.commit()


class QueueService(Service):
    def create(self, data: CreateQueueSchema) -> QueueSchema:
        if data.topic_id is not None:
            get_model(model=Topic, filters={"id": data.topic_id}, session=self.session)

        if data.dead_queue_id is not None:
            get_model(model=Queue, filters={"id": data.dead_queue_id}, session=self.session)

        now = datetime.utcnow()
        queue = Queue(
            id=data.id,
            topic_id=data.topic_id,
            dead_queue_id=data.dead_queue_id,
            ack_deadline_seconds=data.ack_deadline_seconds,
            message_retention_seconds=data.message_retention_seconds,
            message_filters=data.message_filters,
            message_max_deliveries=data.message_max_deliveries,
            delivery_delay_seconds=data.delivery_delay_seconds,
            created_at=now,
            updated_at=now,
        )
        self.session.add(queue)
        try:
            self.session.commit()
        except IntegrityError:
            raise AlreadyExistsError("This queue already exists")
        return QueueSchema.from_orm(queue)

    def update(self, id: str, data: UpdateQueueSchema) -> QueueSchema:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)

        if data.topic_id is not None:
            get_model(model=Topic, filters={"id": data.topic_id}, session=self.session)

        if data.dead_queue_id is not None:
            get_model(model=Queue, filters={"id": data.dead_queue_id}, session=self.session)

        queue.topic_id = data.topic_id
        queue.dead_queue_id = data.dead_queue_id
        queue.ack_deadline_seconds = data.ack_deadline_seconds
        queue.message_retention_seconds = data.message_retention_seconds
        queue.message_filters = data.message_filters
        queue.message_max_deliveries = data.message_max_deliveries
        queue.delivery_delay_seconds = data.delivery_delay_seconds
        queue.created_at = queue.created_at
        queue.updated_at = datetime.utcnow()
        self.session.commit()
        return QueueSchema.from_orm(queue)

    def get(self, id: str) -> QueueSchema:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)
        return QueueSchema.from_orm(queue)

    def list(self, filters: dict | None, offset: int | None, limit: int | None) -> ListQueueSchema:
        queues = list_model(
            model=Queue, filters=filters, offset=offset, limit=limit, order_by=Queue.id, session=self.session
        )
        return ListQueueSchema(data=[QueueSchema.from_orm(queue) for queue in queues])

    def delete(self, id: str) -> None:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)
        self.session.query(Queue).filter_by(id=queue.id).delete()
        self.session.commit()

    def stats(self, id: str) -> QueueStatsSchema:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)

        now = datetime.utcnow()
        filters = get_filters_for_consume(queue, now)
        num_undelivered_messages = self.session.query(Message).filter(*filters).count()
        oldest_unacked_message_age_seconds = 0
        oldest_unacked_message = (
            self.session.query(Message).filter(*filters).order_by(Message.created_at).first()
        )
        if oldest_unacked_message is not None:
            oldest_unacked_message_age_seconds = (now - oldest_unacked_message.created_at).total_seconds()

        return QueueStatsSchema(
            num_undelivered_messages=num_undelivered_messages,
            oldest_unacked_message_age_seconds=oldest_unacked_message_age_seconds,
        )

    def purge(self, id: str) -> None:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)
        self.session.query(Message).filter_by(queue_id=queue.id).delete()
        self.session.commit()

    def _cleanup_expired_messages(self, queue: QueueSchema) -> None:
        now = datetime.utcnow()

        expired_at_filter = [Message.queue_id == queue.id, Message.expired_at <= now]
        self.session.query(Message).filter(*expired_at_filter).delete()

    def _cleanup_move_messages_to_dead_queue(self, queue: QueueSchema) -> None:
        if queue.message_max_deliveries is None or queue.dead_queue_id is None:
            return

        dead_queue = get_model(model=Queue, filters={"id": queue.dead_queue_id}, session=self.session)

        delivery_attempts_filter = [
            Message.queue_id == queue.id,
            Message.delivery_attempts >= queue.message_max_deliveries,
        ]
        now = datetime.utcnow()
        scheduled_at = now
        if dead_queue.delivery_delay_seconds is not None:
            scheduled_at = now + timedelta(seconds=dead_queue.delivery_delay_seconds)
        update_data = {
            "queue_id": queue.dead_queue_id,
            "delivery_attempts": 0,
            "expired_at": now + timedelta(seconds=dead_queue.message_retention_seconds),
            "scheduled_at": scheduled_at,
            "updated_at": now,
        }
        self.session.query(Message).filter(*delivery_attempts_filter).update(
            update_data, synchronize_session=False
        )

    def cleanup(self, id: str) -> None:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)

        self._cleanup_expired_messages(queue=queue)
        self._cleanup_move_messages_to_dead_queue(queue=queue)

        self.session.commit()

    def redrive(self, id: str, data: RedriveQueueSchema) -> None:
        queue = get_model(model=Queue, filters={"id": id}, session=self.session)
        destination_queue = get_model(
            model=Queue, filters={"id": data.destination_queue_id}, session=self.session
        )
        now = datetime.utcnow()
        scheduled_at = now
        if destination_queue.delivery_delay_seconds is not None:
            scheduled_at = now + timedelta(seconds=destination_queue.delivery_delay_seconds)
        filters = get_filters_for_consume(queue, now)
        update_data = {
            "queue_id": destination_queue.id,
            "delivery_attempts": 0,
            "expired_at": now + timedelta(seconds=destination_queue.message_retention_seconds),
            "scheduled_at": scheduled_at,
            "updated_at": now,
        }
        self.session.query(Message).filter(*filters).update(update_data, synchronize_session=False)
        self.session.commit()


class MessageService(Service):
    def _should_message_be_created_on_queue(
        self, queue_filters: dict[str, list[Any]] | None, message_attributes: dict | None
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

    def create(self, topic_id: str, data: CreateMessageSchema) -> ListMessageSchema:
        result = ListMessageSchema(data=[])
        topic = get_model(model=Topic, filters={"id": topic_id}, session=self.session)
        queues = list_model(
            model=Queue,
            filters={"topic_id": topic.id},
            offset=None,
            limit=None,
            order_by=Queue.id,
            session=self.session,
        )
        if not queues:
            return result

        for queue in queues:
            if self._should_message_be_created_on_queue(queue.message_filters, data.attributes) is False:
                continue

            now = datetime.utcnow()
            scheduled_at = now
            if queue.delivery_delay_seconds is not None:
                scheduled_at = now + timedelta(seconds=queue.delivery_delay_seconds)
            message = Message(
                id=uuid.uuid4().hex,
                queue_id=queue.id,
                data=data.data,
                attributes=data.attributes,
                delivery_attempts=0,
                expired_at=now + timedelta(seconds=queue.message_retention_seconds),
                scheduled_at=scheduled_at,
                created_at=now,
                updated_at=now,
            )
            self.session.add(message)
            result.data.append(MessageSchema.from_orm(message))

        self.session.commit()
        return result

    def list_for_consume(self, queue_id: str, limit: int) -> ListMessageSchema:
        queue = get_model(model=Queue, filters={"id": queue_id}, session=self.session)
        now = datetime.utcnow()
        filters = get_filters_for_consume(queue, now)
        data = []
        messages = (
            self.session.query(Message).filter(*filters).with_for_update(skip_locked=True).limit(limit).all()
        )
        for message in messages:
            message.delivery_attempts += 1
            message.scheduled_at = now + timedelta(seconds=queue.ack_deadline_seconds)
            message.updated_at = now
            data.append(MessageSchema.from_orm(message))

        self.session.commit()
        return ListMessageSchema(data=data)

    def ack(self, id: str) -> None:
        self.session.query(Message).filter_by(id=id).delete()
        self.session.commit()

    def nack(self, id: str) -> None:
        try:
            message = get_model(model=Message, filters={"id": id}, session=self.session)
        except NotFoundError:
            return

        now = datetime.utcnow()
        message.scheduled_at = now
        message.updated_at = now
        self.session.commit()


class HealthService(Service):
    def check(self) -> HealthSchema:
        success = True
        try:
            self.session.query(text("1")).from_statement(text("SELECT 1")).all()
        except Exception:
            success = False

        return HealthSchema(success=success)
