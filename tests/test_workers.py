from datetime import datetime, timedelta

from fastqueue.models import Message
from fastqueue.workers import queue_cleanup_task
from tests.factories import MessageFactory


def test_queue_cleanup(session, queue):
    messages = MessageFactory.build_batch(5, queue_id=queue.id)
    for message in messages:
        message.expired_at = datetime.utcnow() - timedelta(seconds=1)
        session.add(message)
    session.commit()

    assert session.query(Message).filter_by(queue_id=queue.id).count() == 5

    assert queue_cleanup_task() is None

    assert session.query(Message).filter_by(queue_id=queue.id).count() == 0
