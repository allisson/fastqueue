import pytest

from fastqueue.exceptions import NotFoundError
from fastqueue.schemas import CreateQueueSchema, CreateTopicSchema, UpdateQueueSchema
from fastqueue.services import QueueService, TopicService


def test_topic_service_create(session):
    id = "my_topic"
    data = CreateTopicSchema(id=id)

    result = TopicService.create(data, session=session)

    assert result.id == id
    assert result.created_at


def test_topic_service_get(session, topic):
    result = TopicService.get(topic.id, session=session)

    assert result.id == topic.id
    assert result.created_at


def test_topic_service_get_not_found(session):
    with pytest.raises(NotFoundError):
        TopicService.get("invalid-topic-name", session=session)


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
        message_filters={"attr1": "attr1"},
        dead_letter_max_retries=5,
        dead_letter_min_backoff_seconds=1,
        dead_letter_max_backoff_seconds=5,
    )

    result = QueueService.create(data, session=session)

    assert result.id == data.id
    assert result.topic_id == data.topic_id
    assert result.ack_deadline_seconds == data.ack_deadline_seconds
    assert result.message_retention_seconds == data.message_retention_seconds
    assert result.message_filters == data.message_filters
    assert result.dead_letter_max_retries == data.dead_letter_max_retries
    assert result.dead_letter_min_backoff_seconds == data.dead_letter_min_backoff_seconds
    assert result.dead_letter_max_backoff_seconds == data.dead_letter_max_backoff_seconds
    assert result.created_at
    assert result.updated_at


def test_queue_service_update(session, queue):
    data = UpdateQueueSchema(
        topic_id=queue.topic_id,
        ack_deadline_seconds=60,
        message_retention_seconds=60,
        message_filters=None,
        dead_letter_max_retries=None,
        dead_letter_min_backoff_seconds=None,
        dead_letter_max_backoff_seconds=None,
    )

    result = QueueService.update(queue.id, data, session=session)

    assert result.id == queue.id
    assert result.topic_id == data.topic_id
    assert result.ack_deadline_seconds == data.ack_deadline_seconds
    assert result.message_retention_seconds == data.message_retention_seconds
    assert result.message_filters == data.message_filters
    assert result.dead_letter_max_retries == data.dead_letter_max_retries
    assert result.dead_letter_min_backoff_seconds == data.dead_letter_min_backoff_seconds
    assert result.dead_letter_max_backoff_seconds == data.dead_letter_max_backoff_seconds
    assert result.created_at
    assert result.updated_at


def test_queue_service_get(session, queue):
    result = QueueService.get(queue.id, session=session)

    assert result.id == queue.id
    assert result.topic_id == queue.topic_id
    assert result.ack_deadline_seconds == queue.ack_deadline_seconds
    assert result.message_retention_seconds == queue.message_retention_seconds
    assert result.message_filters == queue.message_filters
    assert result.dead_letter_max_retries == queue.dead_letter_max_retries
    assert result.dead_letter_min_backoff_seconds == queue.dead_letter_min_backoff_seconds
    assert result.dead_letter_max_backoff_seconds == queue.dead_letter_max_backoff_seconds
    assert result.created_at
    assert result.updated_at


def test_queue_service_delete(session, queue):
    assert QueueService.delete(queue.id, session=session) is None

    with pytest.raises(NotFoundError):
        QueueService.get(queue.id, session=session)


def test_queue_service_delete_not_found(session):
    with pytest.raises(NotFoundError):
        QueueService.delete("invalid-queue-name", session=session)
