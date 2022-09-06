from datetime import datetime, timedelta
from time import sleep

import pytest

from fastqueue.exceptions import NotFoundError
from fastqueue.schemas import (
    CreateMessageSchema,
    CreateQueueSchema,
    CreateTopicSchema,
    UpdateMessageSchema,
    UpdateQueueSchema,
)
from fastqueue.services import MessageService, QueueService, TopicService
from tests.factories import MessageFactory, QueueFactory, TopicFactory


def test_topic_service_create(session):
    id = "my_topic"
    data = CreateTopicSchema(id=id)

    result = TopicService.create(data, session=session)

    assert result.id == id
    assert result.created_at


def test_topic_service_get_model(session, topic):
    result = TopicService.get_model(topic.id, session=session)

    assert result.id == topic.id
    assert result.created_at


def test_topic_service_get(session, topic):
    result = TopicService.get(topic.id, session=session)

    assert result.id == topic.id
    assert result.created_at


def test_topic_service_get_not_found(session):
    with pytest.raises(NotFoundError):
        TopicService.get("invalid-topic-name", session=session)


def test_topic_service_list(session):
    topics = TopicFactory.build_batch(5)
    for topic in topics:
        session.add(topic)
    session.commit()

    result = TopicService.list(filters=None, offset=0, limit=10, session=session)

    assert len(result.data) == 5

    result = TopicService.list(filters=None, offset=10, limit=10, session=session)

    assert len(result.data) == 0


def test_topic_service_delete(session, topic):
    assert TopicService.delete(topic.id, session=session) is None

    with pytest.raises(NotFoundError):
        TopicService.get(topic.id, session=session)


def test_topic_service_delete_not_found(session):
    with pytest.raises(NotFoundError):
        TopicService.delete("invalid-topic-name", session=session)


def test_queue_service_create(session, topic):
    data = CreateQueueSchema(
        id="my-queue",
        topic_id=topic.id,
        ack_deadline_seconds=30,
        message_retention_seconds=604800,
        message_filters={"attr1": ["attr1"]},
        message_max_deliveries=5,
    )

    result = QueueService.create(data, session=session)

    assert result.id == data.id
    assert result.topic_id == data.topic_id
    assert result.ack_deadline_seconds == data.ack_deadline_seconds
    assert result.message_retention_seconds == data.message_retention_seconds
    assert result.message_filters == data.message_filters
    assert result.message_max_deliveries == data.message_max_deliveries
    assert result.created_at
    assert result.updated_at


def test_queue_service_update(session, queue):
    data = UpdateQueueSchema(
        topic_id=queue.topic_id,
        ack_deadline_seconds=60,
        message_retention_seconds=600,
        message_filters=None,
        message_max_deliveries=None,
    )

    result = QueueService.update(queue.id, data, session=session)

    assert result.id == queue.id
    assert result.topic_id == data.topic_id
    assert result.ack_deadline_seconds == data.ack_deadline_seconds
    assert result.message_retention_seconds == data.message_retention_seconds
    assert result.message_filters == data.message_filters
    assert result.message_max_deliveries == data.message_max_deliveries
    assert result.created_at
    assert result.updated_at


def test_queue_service_get_model(session, queue):
    result = QueueService.get_model(queue.id, session=session)

    assert result.id == queue.id
    assert result.topic_id == queue.topic_id
    assert result.ack_deadline_seconds == queue.ack_deadline_seconds
    assert result.message_retention_seconds == queue.message_retention_seconds
    assert result.message_filters == queue.message_filters
    assert result.message_max_deliveries == queue.message_max_deliveries
    assert result.created_at
    assert result.updated_at


def test_queue_service_get(session, queue):
    result = QueueService.get(queue.id, session=session)

    assert result.id == queue.id
    assert result.topic_id == queue.topic_id
    assert result.ack_deadline_seconds == queue.ack_deadline_seconds
    assert result.message_retention_seconds == queue.message_retention_seconds
    assert result.message_filters == queue.message_filters
    assert result.message_max_deliveries == queue.message_max_deliveries
    assert result.created_at
    assert result.updated_at


def test_queue_service_list(session, topic):
    queues = QueueFactory.build_batch(5)
    for queue in queues:
        queue.topic_id = topic.id
        session.add(queue)
    session.commit()

    result = QueueService.list(filters=None, offset=0, limit=10, session=session)

    assert len(result.data) == 5

    result = QueueService.list(filters=None, offset=10, limit=10, session=session)

    assert len(result.data) == 0


def test_queue_service_delete(session, queue):
    assert QueueService.delete(queue.id, session=session) is None

    with pytest.raises(NotFoundError):
        QueueService.get(queue.id, session=session)


def test_queue_service_delete_not_found(session):
    with pytest.raises(NotFoundError):
        QueueService.delete("invalid-queue-name", session=session)


@pytest.mark.parametrize(
    "queue_filters,message_attributes,expected",
    [
        ({"attr1": [1]}, {"attr1": 1}, True),
        ({"attr1": [1]}, {"attr1": "1"}, False),
        ({"attr1": [1, 2]}, {"attr1": 1}, True),
        ({"attr1": [1, 2]}, {"attr1": 2}, True),
        ({"attr1": [1]}, {"attr2": 1}, False),
        ({"attr1": [1], "attr2": [2]}, {"attr1": 1}, False),
        ({"attr1": [1], "attr2": [2]}, {"attr1": 1, "attr2": 2}, True),
        ({"attr1": [1], "attr2": [2]}, {"attr1": 1, "attr2": 2, "attr3": 3}, True),
        ({"attr1": [1, 2], "attr2": [1, 2]}, {"attr1": 1, "attr2": 2, "attr3": 3}, True),
        (None, {"attr1": 1}, True),
        ({"attr1": [1]}, None, False),
        (None, None, True),
    ],
)
def test_message_service_should_message_be_created_on_queue(queue_filters, message_attributes, expected):
    assert MessageService._should_message_be_created_on_queue(queue_filters, message_attributes) is expected


def test_message_service_create(session, topic):
    queues = QueueFactory.build_batch(5)
    for queue in queues:
        queue.topic_id = topic.id
        session.add(queue)
    session.commit()
    queue_names = [queue.id for queue in queues]
    data = CreateMessageSchema(
        data={"message": "Hello World"}, attributes={"attr1": "attr1", "attr2": "attr2"}
    )

    result = MessageService.create(topic_id=queue.topic_id, data=data, session=session)

    assert len(result.data) == 5
    for message in result.data:
        assert message.queue_id in queue_names
        assert message.data == data.data
        assert message.attributes == data.attributes


def test_message_service_update(session, message):
    data = UpdateMessageSchema(
        delivery_attempts=1,
        scheduled_at=datetime.utcnow() + timedelta(seconds=30),
    )

    result = MessageService.update(message.id, data, session=session)

    assert str(result.id) == message.id
    assert result.queue_id == message.queue_id
    assert result.data == message.data
    assert result.attributes == message.attributes
    assert result.delivery_attempts == message.delivery_attempts
    assert result.created_at
    assert result.updated_at


def test_message_service_get_model(session, message):
    result = MessageService.get_model(id=message.id, session=session)

    assert result.id == message.id
    assert result.queue_id == message.queue_id
    assert result.data == message.data
    assert result.attributes == message.attributes
    assert result.delivery_attempts == message.delivery_attempts
    assert result.expired_at == message.expired_at
    assert result.scheduled_at == message.scheduled_at
    assert result.created_at
    assert result.updated_at


def test_message_service_get(session, message):
    result = MessageService.get(id=message.id, session=session)

    assert str(result.id) == message.id
    assert result.queue_id == message.queue_id
    assert result.data == message.data
    assert result.attributes == message.attributes
    assert result.delivery_attempts == message.delivery_attempts
    assert result.created_at
    assert result.updated_at


def test_message_service_list(session, queue):
    messages = MessageFactory.build_batch(5)
    for message in messages:
        message.queue_id = queue.id
        session.add(message)
    session.commit()

    result = MessageService.list(filters=None, offset=0, limit=10, session=session)

    assert len(result.data) == 5

    result = MessageService.list(filters=None, offset=10, limit=10, session=session)

    assert len(result.data) == 0


def test_message_service_list_for_consume(session, queue):
    queue.ack_deadline_seconds = 1
    queue.message_max_deliveries = None
    session.commit()
    data = CreateMessageSchema(data={"message": "Hello World"}, attributes={"attr1": "attr1"})
    MessageService.create(topic_id=queue.topic_id, data=data, session=session)
    MessageService.create(topic_id=queue.topic_id, data=data, session=session)
    now = datetime.utcnow()

    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 2
    for message in result.data:
        assert message.queue_id == queue.id
        assert message.data == data.data
        assert message.attributes == data.attributes
        assert message.delivery_attempts == 1
        assert message.scheduled_at > now
        assert message.expired_at > now

    sleep(0.5)
    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 0

    sleep(0.5)
    now = datetime.utcnow()
    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 2
    for message in result.data:
        assert message.queue_id == queue.id
        assert message.data == data.data
        assert message.attributes == data.attributes
        assert message.delivery_attempts == 2
        assert message.scheduled_at > now
        assert message.expired_at > now


def test_message_service_list_for_consume_with_message_max_deliveries(session, queue):
    queue.ack_deadline_seconds = 1
    queue.message_max_deliveries = 1
    session.commit()
    data = CreateMessageSchema(data={"message": "Hello World"}, attributes={"attr1": "attr1"})
    MessageService.create(topic_id=queue.topic_id, data=data, session=session)
    MessageService.create(topic_id=queue.topic_id, data=data, session=session)
    now = datetime.utcnow()

    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 2
    for message in result.data:
        assert message.queue_id == queue.id
        assert message.data == data.data
        assert message.attributes == data.attributes
        assert message.delivery_attempts == 1
        assert message.scheduled_at > now
        assert message.expired_at > now

    sleep(0.5)
    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 0

    sleep(0.5)
    now = datetime.utcnow()
    result = MessageService.list_for_consume(queue_id=queue.id, limit=10, session=session)
    assert len(result.data) == 0
