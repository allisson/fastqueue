def test_topic(topic):
    expected_repr = f"User(id='{topic.id}')"
    assert repr(topic) == expected_repr
    assert str(topic) == expected_repr


def test_queue(queue):
    expected_repr = f"Queue(id='{queue.id}', topic_id='{queue.topic_id}')"
    assert repr(queue) == expected_repr
    assert str(queue) == expected_repr


def test_message(message):
    expected_repr = f"Message(id='{message.id}', queue_id='{message.queue_id}')"
    assert repr(message) == expected_repr
    assert str(message) == expected_repr
