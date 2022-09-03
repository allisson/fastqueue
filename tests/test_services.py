import pytest

from fastqueue.exceptions import NotFoundError
from fastqueue.schemas import CreateTopicSchema
from fastqueue.services import TopicService


def test_topic_service_create(session):
    id = "my_topic"
    data = CreateTopicSchema(id=id)
    service = TopicService()

    result = service.create(data, session=session)

    assert result.id == id
    assert result.created_at


def test_topic_service_get(session, topic):
    service = TopicService()

    result = service.get(topic.id, session=session)

    assert result.id == topic.id
    assert result.created_at


def test_topic_service_delete(session, topic):
    service = TopicService()

    assert service.delete(topic.id, session=session) is None

    with pytest.raises(NotFoundError):
        service.get(topic.id, session=session)
