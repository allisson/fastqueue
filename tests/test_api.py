from datetime import datetime, timedelta

from fastapi import status

from tests.factories import MessageFactory, QueueFactory, TopicFactory


def test_create_topic(session, client):
    data = {"id": "my-topic"}

    response = client.post("/topics", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["id"] == data["id"]


def test_create_topic_already_exists(session, topic, client):
    data = {"id": topic.id}

    response = client.post("/topics", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data == {"detail": "This topic already exists"}


def test_get_topic(session, topic, client):
    response = client.get(f"/topics/{topic.id}")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["id"] == topic.id


def test_get_topic_not_found(session, client):
    response = client.get("/topics/not-found-topic")
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {"detail": "Topic not found"}


def test_delete_topic(session, topic, client):
    response = client.delete(f"/topics/{topic.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_list_topics(session, client):
    topics = TopicFactory.build_batch(5)
    for topic in topics:
        session.add(topic)
    session.commit()

    response = client.get("/topics")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 5


def test_create_queue(session, topic, client):
    data = {
        "id": "my-queue",
        "topic_id": topic.id,
        "ack_deadline_seconds": 60,
        "message_retention_seconds": 3600,
    }

    response = client.post("/queues", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["id"] == data["id"]


def test_create_queue_already_exists(session, queue, client):
    data = {
        "id": queue.id,
        "topic_id": queue.topic_id,
        "ack_deadline_seconds": 60,
        "message_retention_seconds": 3600,
    }

    response = client.post("/queues", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_data == {"detail": "This queue already exists"}


def test_get_queue(session, queue, client):
    response = client.get(f"/queues/{queue.id}")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["id"] == queue.id


def test_get_queue_not_found(session, client):
    response = client.get("/queues/not-found-queue")
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {"detail": "Queue not found"}


def test_update_queue(session, queue, client):
    data = {
        "topic_id": queue.topic_id,
        "ack_deadline_seconds": 10,
        "message_retention_seconds": 600,
        "message_filters": {"attr1": ["attr1"]},
        "message_max_deliveries": 10,
    }

    response = client.put(f"/queues/{queue.id}", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["id"] == queue.id
    assert response_data["topic_id"] == data["topic_id"]
    assert response_data["ack_deadline_seconds"] == data["ack_deadline_seconds"]
    assert response_data["message_retention_seconds"] == data["message_retention_seconds"]
    assert response_data["message_filters"] == data["message_filters"]
    assert response_data["message_max_deliveries"] == data["message_max_deliveries"]


def test_update_queue_not_found(session, client):
    data = {
        "topic_id": "topic_id",
        "ack_deadline_seconds": 10,
        "message_retention_seconds": 600,
        "message_filters": {"attr1": ["attr1"]},
        "message_max_deliveries": 10,
    }

    response = client.put("/queues/not-found-queue", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {"detail": "Queue not found"}


def test_update_queue_not_found_topic(session, queue, client):
    data = {
        "topic_id": "not_topic_id",
        "ack_deadline_seconds": 10,
        "message_retention_seconds": 600,
        "message_filters": {"attr1": ["attr1"]},
        "message_max_deliveries": 10,
    }

    response = client.put(f"/queues/{queue.id}", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {"detail": "Topic not found"}


def test_get_queue_stats(session, queue, client):
    created_at = datetime.utcnow() - timedelta(seconds=10)
    messages = MessageFactory.build_batch(5, queue_id=queue.id, created_at=created_at)
    for message in messages:
        session.add(message)
    session.commit()

    response = client.get(f"/queues/{queue.id}/stats")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data == {"num_undelivered_messages": 5, "oldest_unacked_message_age_seconds": 10}


def test_delete_queue(session, queue, client):
    response = client.delete(f"/queues/{queue.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_queue_not_found(session, client):
    response = client.delete("/queues/not-found-queue")
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {"detail": "Queue not found"}


def test_list_queues(session, topic, client):
    queues = QueueFactory.build_batch(5, topic_id=topic.id)
    for queue in queues:
        session.add(queue)
    session.commit()

    response = client.get("/queues")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 5


def test_create_message(session, queue, client):
    data = {
        "data": {"message": "Hello World"},
        "attributes": {"attr1": "attr1"},
    }

    response = client.post(f"/topics/{queue.topic_id}/messages", json=data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response_data["data"]) == 1
    for message in response_data["data"]:
        assert message["queue_id"] == queue.id
        assert message["data"] == data["data"]
        assert message["attributes"] == data["attributes"]


def test_list_messages_for_consume(session, message, client):
    response = client.get(f"/queues/{message.queue_id}/messages")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 1
    for m in response_data["data"]:
        assert m["queue_id"] == message.queue_id
        assert m["data"] == message.data
        assert m["attributes"] == message.attributes


def test_ack_message(session, message, client):
    response = client.post(f"/messages/{message.id}/ack")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_nack_message(session, message, client):
    response = client.post(f"/messages/{message.id}/nack")

    assert response.status_code == status.HTTP_204_NO_CONTENT
