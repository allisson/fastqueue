# fastqueue
Simple queue system based on FastAPI and PostgreSQL.

## Quickstart

Let's start with the basic concepts, we have three main entities that we must know to start:

- Topic: A named resource to which messages are sent.
- Queue: A named resource representing a queue that receives messages from topics.
- Message: The data that a publisher sends to a topic is eventually delivered to queues.

### Install httpie cli

See the instructions here: https://httpie.io/docs/cli/installation.

### Run the local PostgreSQL server

To run the server it is necessary to have a database available from PostgreSQL:

```bash
docker run --name postgres-fastqueue \
    --restart unless-stopped \
    -e POSTGRES_USER=fastqueue \
    -e POSTGRES_PASSWORD=fastqueue \
    -e POSTGRES_DB=fastqueue \
    -p 5432:5432 \
    -d postgres:14-alpine
```

### Run the database migration

The database migration is responsible to create the database schema.

```bash
docker run --rm \
    -e FASTQUEUE_DATABASE_URL='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    --network="host" \
    fastqueue db-migrate
```

### Run the worker

The worker is responsible for cleanup the messages from queues (remove expired messages and move to dead queue if configured).

```bash
docker run --name fastqueue-worker \
    --restart unless-stopped \
    -e FASTQUEUE_DATABASE_URL='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    -e FASTQUEUE_QUEUE_CLEANUP_INTERVAL_SECONDS=60 \
    --network="host" \
    fastqueue worker
```

### Run the server

The server is responsible to deliver the rest API.

```bash
docker run --name fastqueue-server \
    --restart unless-stopped \
    -e FASTQUEUE_DATABASE_URL='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    -e FASTQUEUE_SERVER_PORT=8000 \
    -e FASTQUEUE_SERVER_NUM_WORKERS=1 \
    --network="host" \
    fastqueue server
```

### Create a new topic

```bash
http POST http://localhost:8000/topics id=events
```

```
HTTP/1.1 201 Created
content-length: 57
content-type: application/json
date: Wed, 05 Oct 2022 19:21:30 GMT
server: uvicorn

{
    "created_at": "2022-10-05T19:21:30.651029",
    "id": "events"
}
```

```bash
http GET http://localhost:8000/topics
```

```
HTTP/1.1 200 OK
content-length: 68
content-type: application/json
date: Wed, 05 Oct 2022 19:22:59 GMT
server: uvicorn

{
    "data": [
        {
            "created_at": "2022-10-05T19:21:30.651029",
            "id": "events"
        }
    ]
}
```

### Create a new queue

```bash
http POST http://localhost:8000/queues id=all-events topic_id=events ack_deadline_seconds=30 message_retention_seconds=1209600
```

```
HTTP/1.1 201 Created
content-length: 259
content-type: application/json
date: Wed, 05 Oct 2022 19:27:16 GMT
server: uvicorn

{
    "ack_deadline_seconds": 30,
    "created_at": "2022-10-05T19:27:17.456611",
    "dead_queue_id": null,
    "id": "all-events",
    "message_filters": null,
    "message_max_deliveries": null,
    "message_retention_seconds": 1209600,
    "topic_id": "events",
    "updated_at": "2022-10-05T19:27:17.456611"
}
```

### Create a new message

```bash
http POST http://localhost:8000/topics/events/messages data:='{"event_name": "event1", "success": true}' attributes:='{"event_name": "event1"}'
```

```
HTTP/1.1 201 Created
content-length: 355
content-type: application/json
date: Wed, 05 Oct 2022 19:36:05 GMT
server: uvicorn

{
    "data": [
        {
            "attributes": {
                "event_name": "event1"
            },
            "created_at": "2022-10-05T19:36:06.501056",
            "data": {
                "event_name": "event1",
                "success": true
            },
            "delivery_attempts": 0,
            "expired_at": "2022-10-19T19:36:06.501056",
            "id": "671cfac2-252c-4c22-9abc-28809a4f9fe8",
            "queue_id": "all-events",
            "scheduled_at": "2022-10-05T19:36:06.501056",
            "updated_at": "2022-10-05T19:36:06.501056"
        }
    ]
}
```

```bash
http GET http://localhost:8000/queues/all-events/stats
```

```
HTTP/1.1 200 OK
content-length: 71
content-type: application/json
date: Wed, 05 Oct 2022 19:38:51 GMT
server: uvicorn

{
    "num_undelivered_messages": 1,
    "oldest_unacked_message_age_seconds": 165
}
```

### Consume messages from the queue

```bash
http GET http://localhost:8000/queues/all-events/messages
```

```
HTTP/1.1 200 OK
content-length: 355
content-type: application/json
date: Wed, 05 Oct 2022 19:43:53 GMT
server: uvicorn

{
    "data": [
        {
            "attributes": {
                "event_name": "event1"
            },
            "created_at": "2022-10-05T19:36:06.501056",
            "data": {
                "event_name": "event1",
                "success": true
            },
            "delivery_attempts": 1,
            "expired_at": "2022-10-19T19:36:06.501056",
            "id": "671cfac2-252c-4c22-9abc-28809a4f9fe8",
            "queue_id": "all-events",
            "scheduled_at": "2022-10-05T19:44:24.679562",
            "updated_at": "2022-10-05T19:43:54.679562"
        }
    ]
}
```

```bash
http PUT http://localhost:8000/messages/671cfac2-252c-4c22-9abc-28809a4f9fe8/nack
```

```
HTTP/1.1 204 No Content
content-type: application/json
date: Wed, 05 Oct 2022 19:48:56 GMT
server: uvicorn
```

```bash
http GET http://localhost:8000/queues/all-events/messages
```

```
HTTP/1.1 200 OK
content-length: 355
content-type: application/json
date: Wed, 05 Oct 2022 19:49:33 GMT
server: uvicorn

{
    "data": [
        {
            "attributes": {
                "event_name": "event1"
            },
            "created_at": "2022-10-05T19:36:06.501056",
            "data": {
                "event_name": "event1",
                "success": true
            },
            "delivery_attempts": 2,
            "expired_at": "2022-10-19T19:36:06.501056",
            "id": "671cfac2-252c-4c22-9abc-28809a4f9fe8",
            "queue_id": "all-events",
            "scheduled_at": "2022-10-05T19:50:03.820722",
            "updated_at": "2022-10-05T19:49:33.820722"
        }
    ]
}
```

```bash
http PUT http://localhost:8000/messages/671cfac2-252c-4c22-9abc-28809a4f9fe8/ack
```

```
HTTP/1.1 204 No Content
content-type: application/json
date: Wed, 05 Oct 2022 19:50:06 GMT
server: uvicorn
```

```bash
http GET http://localhost:8000/queues/all-events/messages
```

```
HTTP/1.1 200 OK
content-length: 11
content-type: application/json
date: Wed, 05 Oct 2022 19:50:34 GMT
server: uvicorn

{
    "data": []
}
```
