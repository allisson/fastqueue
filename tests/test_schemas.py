import pytest
from pydantic import ValidationError

from fastqueue.schemas import CreateQueueSchema, UpdateQueueSchema


@pytest.mark.parametrize(
    "dead_queue_id,message_max_deliveries,expected",
    [
        (
            "my-dead-queue-1",
            None,
            [
                {
                    "loc": ("__root__",),
                    "msg": "message_max_deliveries is required for dead queue support",
                    "type": "value_error",
                }
            ],
        ),
        (
            None,
            5,
            [
                {
                    "loc": ("__root__",),
                    "msg": "dead_queue_id is required for dead queue support",
                    "type": "value_error",
                }
            ],
        ),
    ],
)
def test_create_queue_schema(dead_queue_id, message_max_deliveries, expected):
    data = {
        "id": "my-queue-1",
        "dead_queue_id": dead_queue_id,
        "ack_deadline_seconds": 60,
        "message_retention_seconds": 600,
        "message_max_deliveries": message_max_deliveries,
    }

    with pytest.raises(ValidationError) as excinfo:
        CreateQueueSchema(**data)

    assert excinfo.value.errors() == expected


@pytest.mark.parametrize(
    "dead_queue_id,message_max_deliveries,expected",
    [
        (
            "my-dead-queue-1",
            None,
            [
                {
                    "loc": ("__root__",),
                    "msg": "message_max_deliveries is required for dead queue support",
                    "type": "value_error",
                }
            ],
        ),
        (
            None,
            5,
            [
                {
                    "loc": ("__root__",),
                    "msg": "dead_queue_id is required for dead queue support",
                    "type": "value_error",
                }
            ],
        ),
    ],
)
def test_update_queue_schema(dead_queue_id, message_max_deliveries, expected):
    data = {
        "dead_queue_id": dead_queue_id,
        "ack_deadline_seconds": 60,
        "message_retention_seconds": 600,
        "message_max_deliveries": message_max_deliveries,
    }

    with pytest.raises(ValidationError) as excinfo:
        UpdateQueueSchema(**data)

    assert excinfo.value.errors() == expected
