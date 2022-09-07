from datetime import datetime, timedelta

import factory

from fastqueue.models import Message, Queue, Topic

default_message_retention_seconds = 604800
default_ack_deadline_seconds = 30


def expired_at():
    return datetime.utcnow() + timedelta(seconds=default_message_retention_seconds)


def scheduled_at():
    return datetime.utcnow() + timedelta(seconds=default_ack_deadline_seconds)


class TopicFactory(factory.Factory):
    class Meta:
        model = Topic

    id = factory.Sequence(lambda n: "topic_%s" % n)
    created_at = factory.LazyFunction(datetime.utcnow)


class QueueFactory(factory.Factory):
    class Meta:
        model = Queue

    id = factory.Sequence(lambda n: "queue_%s" % n)
    ack_deadline_seconds = default_ack_deadline_seconds
    message_retention_seconds = default_message_retention_seconds
    message_max_deliveries = None
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class MessageFactory(factory.Factory):
    class Meta:
        model = Message

    id = factory.Faker("uuid4")
    data = {"message": "Hello"}
    delivery_attempts = 0
    expired_at = factory.LazyFunction(expired_at)
    scheduled_at = factory.LazyFunction(scheduled_at)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
