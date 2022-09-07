import pytest
from fastapi.testclient import TestClient

from fastqueue.api import app
from fastqueue.database import Base, engine, SessionLocal
from fastqueue.models import Message, Queue, Topic
from tests.factories import MessageFactory, QueueFactory, TopicFactory


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def connection():
    connection = engine.connect()
    Base.metadata.create_all(bind=engine)
    yield connection
    Base.metadata.drop_all(bind=engine)
    connection.close()


@pytest.fixture(scope="function")
def session(connection):
    session = SessionLocal(bind=connection)
    yield session
    session.query(Message).delete()
    session.query(Queue).delete()
    session.query(Topic).delete()
    session.commit()
    session.close()


@pytest.fixture
def topic(session):
    topic = TopicFactory()
    session.add(topic)
    session.commit()
    return topic


@pytest.fixture
def queue(session, topic):
    queue = QueueFactory()
    queue.topic_id = topic.id
    session.add(queue)
    session.commit()
    return queue


@pytest.fixture
def message(session, queue):
    message = MessageFactory()
    message.queue_id = queue.id
    session.add(message)
    session.commit()
    return message
