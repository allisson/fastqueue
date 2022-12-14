# fastqueue
Simple queue system based on FastAPI and PostgreSQL.

## Features

- Simple rest api.
- Message filtering support.
- Dead queue support.
- Redrive support (move messages between queues).
- Delay queues support.
- Prometheus metrics support.
- Simplicity, it does the minimum necessary, it will not have an authentication/permission scheme among other things.

## Quickstart

Let's start with the basic concepts, we have three main entities that we must know to start:

- Topic: A named resource to which messages are sent.
- Queue: A named resource representing a queue that receives messages from topics.
- Message: The data that a publisher sends to a topic is eventually delivered to queues.

### Environment variables

See https://github.com/allisson/fastqueue/blob/main/env.sample.default.

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
    -e fastqueue_database_url='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    --network="host" \
    quay.io/allisson/fastqueue db-migrate
```

### Run the worker

The worker is responsible for cleanup the messages from queues (remove expired messages and move to dead queue if configured).

```bash
docker run --name fastqueue-worker \
    --restart unless-stopped \
    -e fastqueue_database_url='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    -e fastqueue_queue_cleanup_interval_seconds=60 \
    --network="host" \
    quay.io/allisson/fastqueue worker
```

### Run the server

The server is responsible to deliver the rest API.

```bash
docker run --name fastqueue-server \
    --restart unless-stopped \
    -e fastqueue_database_url='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    -e fastqueue_server_port=8000 \
    -e fastqueue_server_num_workers=1 \
    --network="host" \
    quay.io/allisson/fastqueue server
```

You can access the api docs at http://localhost:8000/docs or http://localhost:8000/redoc.

### Create a new topic

```bash
curl -i -X 'POST' \
  'http://127.0.0.1:8000/topics' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "events"
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 21:48:24 GMT
server: uvicorn
content-length: 57
content-type: application/json

{
  "id":"events",
  "created_at":"2022-10-05T21:48:24.724341"
}
```

```bash
curl -i -X 'GET' \
  'http://127.0.0.1:8000/topics' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Wed, 05 Oct 2022 21:49:40 GMT
server: uvicorn
content-length: 68
content-type: application/json

{
  "data":[
    {
      "id":"events",
      "created_at":"2022-10-05T21:48:24.724341"
    }
  ]
}
```

### Create a new queue

```bash
curl -i -X 'POST' \
  'http://localhost:8000/queues' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "all-events",
  "topic_id": "events",
  "ack_deadline_seconds": 30,
  "message_retention_seconds": 1209600
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 21:51:43 GMT
server: uvicorn
content-length: 259
content-type: application/json

{
  "id":"all-events",
  "topic_id":"events",
  "dead_queue_id":null,
  "ack_deadline_seconds":30,
  "message_retention_seconds":1209600,
  "message_filters":null,
  "message_max_deliveries":null,
  "delivery_delay_seconds":null,
  "created_at":"2022-10-05T21:51:44.684743",
  "updated_at":"2022-10-05T21:51:44.684743"
}
```

### Create a new message

```bash
curl -i -X 'POST' \
  'http://localhost:8000/topics/events/messages' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": {"event_name": "event1", "success": true},
  "attributes": {"event_name": "event1"}
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 21:54:07 GMT
server: uvicorn
content-length: 355
content-type: application/json

{
  "data":[
    {
      "id":"147d5f58-9dc5-4f69-8ab1-107a799fd731",
      "queue_id":"all-events",
      "data":{
        "event_name":"event1",
        "success":true
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":0,
      "expired_at":"2022-10-19T21:54:08.010379",
      "scheduled_at":"2022-10-05T21:54:08.010379",
      "created_at":"2022-10-05T21:54:08.010379",
      "updated_at":"2022-10-05T21:54:08.010379"
    }
  ]
}
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Wed, 05 Oct 2022 21:55:13 GMT
server: uvicorn
content-length: 70
content-type: application/json

{
  "num_undelivered_messages":1,
  "oldest_unacked_message_age_seconds":66
}
```

### Consume messages from the queue

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Wed, 05 Oct 2022 21:56:07 GMT
server: uvicorn
content-length: 355
content-type: application/json

{
  "data":[
    {
      "id":"147d5f58-9dc5-4f69-8ab1-107a799fd731",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event1"
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":1,
      "expired_at":"2022-10-19T21:54:08.010379",
      "scheduled_at":"2022-10-05T21:56:37.272384",
      "created_at":"2022-10-05T21:54:08.010379",
      "updated_at":"2022-10-05T21:56:07.272384"
    }
  ]
}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/147d5f58-9dc5-4f69-8ab1-107a799fd731/nack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Wed, 05 Oct 2022 21:57:17 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Wed, 05 Oct 2022 21:57:53 GMT
server: uvicorn
content-length: 355
content-type: application/json

{
  "data":[
    {
      "id":"147d5f58-9dc5-4f69-8ab1-107a799fd731",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event1"
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":2,
      "expired_at":"2022-10-19T21:54:08.010379",
      "scheduled_at":"2022-10-05T21:58:24.560500",
      "created_at":"2022-10-05T21:54:08.010379",
      "updated_at":"2022-10-05T21:57:54.560500"
    }
  ]
}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/147d5f58-9dc5-4f69-8ab1-107a799fd731/ack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Wed, 05 Oct 2022 21:58:56 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Wed, 05 Oct 2022 21:59:26 GMT
server: uvicorn
content-length: 11
content-type: application/json

{
  "data":[]
}
```

## Message filtering

We can receive a subset of the messages in the queue using the message_filters field.

```bash
curl -i -X 'POST' \
  'http://localhost:8000/queues' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "filtered-events",
  "topic_id": "events",
  "ack_deadline_seconds": 30,
  "message_retention_seconds": 1209600,
  "message_filters": {
    "event_name": ["event2"]
  }
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 23:42:09 GMT
server: uvicorn
content-length: 285
content-type: application/json

{
  "id":"filtered-events",
  "topic_id":"events",
  "dead_queue_id":null,
  "ack_deadline_seconds":30,
  "message_retention_seconds":1209600,
  "message_filters":{
    "event_name":[
      "event2"
    ]
  },
  "message_max_deliveries":null,
  "delivery_delay_seconds":null,
  "created_at":"2022-10-05T23:42:10.322336",
  "updated_at":"2022-10-05T23:42:10.322336"
}
```

```bash
curl -i -X 'POST' \
  'http://localhost:8000/topics/events/messages' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": {"event_name": "event1", "success": true},
  "attributes": {"event_name": "event1"}
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 23:43:33 GMT
server: uvicorn
content-length: 355
content-type: application/json

{
  "data":[
    {
      "id":"1dd422ad-7d20-4257-94c0-00fc1fbb8092",
      "queue_id":"all-events",
      "data":{
        "event_name":"event1",
        "success":true
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":0,
      "expired_at":"2022-10-19T23:43:33.265369",
      "scheduled_at":"2022-10-05T23:43:33.265369",
      "created_at":"2022-10-05T23:43:33.265369",
      "updated_at":"2022-10-05T23:43:33.265369"
    }
  ]
}
```

```bash
curl -i -X 'POST' \
  'http://localhost:8000/topics/events/messages' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": {"event_name": "event2", "success": true},
  "attributes": {"event_name": "event2"}
}'

HTTP/1.1 201 Created
date: Wed, 05 Oct 2022 23:51:35 GMT
server: uvicorn
content-length: 705
content-type: application/json

{
  "data":[
    {
      "id":"8856ea21-665f-40a1-b576-33fa067c6a7a",
      "queue_id":"all-events",
      "data":{
        "event_name":"event2",
        "success":true
      },
      "attributes":{
        "event_name":"event2"
      },
      "delivery_attempts":0,
      "expired_at":"2022-10-19T23:51:36.175915",
      "scheduled_at":"2022-10-05T23:51:36.175915",
      "created_at":"2022-10-05T23:51:36.175915",
      "updated_at":"2022-10-05T23:51:36.175915"
    },
    {
      "id":"46f9b01c-2a1c-46d9-89a2-0beb2c331ae3",
      "queue_id":"filtered-events",
      "data":{
        "event_name":"event2",
        "success":true
      },
      "attributes":{
        "event_name":"event2"
      },
      "delivery_attempts":0,
      "expired_at":"2022-10-19T23:51:36.176050",
      "scheduled_at":"2022-10-05T23:51:36.176050",
      "created_at":"2022-10-05T23:51:36.176050",
      "updated_at":"2022-10-05T23:51:36.176050"
    }
  ]
}
```

## Dead queue support

The idea of the dead queue is to move messages that could not be processed to another queue, this can be done using the combination of dead_queue_id and message_max_deliveries fields.

```bash
curl -i -X 'POST' \
  'http://localhost:8000/queues' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "all-events-dead",
  "ack_deadline_seconds": 30,
  "message_retention_seconds": 1209600
}'

HTTP/1.1 201 Created
date: Thu, 06 Oct 2022 00:33:03 GMT
server: uvicorn
content-length: 260
content-type: application/json

{
  "id":"all-events-dead",
  "topic_id":null,
  "dead_queue_id":null,
  "ack_deadline_seconds":30,
  "message_retention_seconds":1209600,
  "message_filters":null,
  "message_max_deliveries":null,
  "delivery_delay_seconds":null,
  "created_at":"2022-10-06T00:33:04.707829",
  "updated_at":"2022-10-06T00:33:04.707829"
}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/queues/all-events' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "topic_id": "events",
  "ack_deadline_seconds": 30,
  "message_retention_seconds": 1209600,
  "dead_queue_id": "all-events-dead",
  "message_max_deliveries": 2
}'

HTTP/1.1 200 OK
date: Thu, 06 Oct 2022 01:05:55 GMT
server: uvicorn
content-length: 269
content-type: application/json

{
  "id":"all-events",
  "topic_id":"events",
  "dead_queue_id":"all-events-dead",
  "ack_deadline_seconds":30,
  "message_retention_seconds":1209600,
  "message_filters":null,
  "message_max_deliveries":2,
  "delivery_delay_seconds":null,
  "created_at":"2022-10-05T21:51:44.684743",
  "updated_at":"2022-10-06T01:05:56.066023"
}
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Thu, 06 Oct 2022 01:07:50 GMT
server: uvicorn
content-length: 700
content-type: application/json

{
  "data":[
    {
      "id":"1dd422ad-7d20-4257-94c0-00fc1fbb8092",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event1"
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":1,
      "expired_at":"2022-10-19T23:43:33.265369",
      "scheduled_at":"2022-10-06T01:08:21.408095",
      "created_at":"2022-10-05T23:43:33.265369",
      "updated_at":"2022-10-06T01:07:51.408095"
    },
    {
      "id":"8856ea21-665f-40a1-b576-33fa067c6a7a",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event2"
      },
      "attributes":{
        "event_name":"event2"
      },
      "delivery_attempts":1,
      "expired_at":"2022-10-19T23:51:36.175915",
      "scheduled_at":"2022-10-06T01:08:21.408095",
      "created_at":"2022-10-05T23:51:36.175915",
      "updated_at":"2022-10-06T01:07:51.408095"
    }
  ]
}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/1dd422ad-7d20-4257-94c0-00fc1fbb8092/nack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Thu, 06 Oct 2022 01:09:54 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/8856ea21-665f-40a1-b576-33fa067c6a7a/nack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Thu, 06 Oct 2022 01:10:26 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Thu, 06 Oct 2022 01:10:49 GMT
server: uvicorn
content-length: 700
content-type: application/json

{
  "data":[
    {
      "id":"1dd422ad-7d20-4257-94c0-00fc1fbb8092",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event1"
      },
      "attributes":{
        "event_name":"event1"
      },
      "delivery_attempts":2,
      "expired_at":"2022-10-19T23:43:33.265369",
      "scheduled_at":"2022-10-06T01:11:19.631164",
      "created_at":"2022-10-05T23:43:33.265369",
      "updated_at":"2022-10-06T01:10:49.631164"
    },
    {
      "id":"8856ea21-665f-40a1-b576-33fa067c6a7a",
      "queue_id":"all-events",
      "data":{
        "success":true,
        "event_name":"event2"
      },
      "attributes":{
        "event_name":"event2"
      },
      "delivery_attempts":2,
      "expired_at":"2022-10-19T23:51:36.175915",
      "scheduled_at":"2022-10-06T01:11:19.631164",
      "created_at":"2022-10-05T23:51:36.175915",
      "updated_at":"2022-10-06T01:10:49.631164"
    }
  ]
}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/1dd422ad-7d20-4257-94c0-00fc1fbb8092/nack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Thu, 06 Oct 2022 01:11:34 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/messages/8856ea21-665f-40a1-b576-33fa067c6a7a/nack' \
  -H 'accept: application/json'

HTTP/1.1 204 No Content
date: Thu, 06 Oct 2022 01:12:03 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Thu, 06 Oct 2022 01:13:14 GMT
server: uvicorn
content-length: 69
content-type: application/json

{"num_undelivered_messages":0,"oldest_unacked_message_age_seconds":0}
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events-dead/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Thu, 06 Oct 2022 01:13:43 GMT
server: uvicorn
content-length: 72
content-type: application/json

{"num_undelivered_messages":2,"oldest_unacked_message_age_seconds":5410}
```

## Redrive support

With redrive you can move messages between queues, we usually use this feature to move messages from the dead queue to the original queue.

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Fri, 07 Oct 2022 20:13:15 GMT
server: uvicorn
content-length: 69
content-type: application/json

{"num_undelivered_messages":0,"oldest_unacked_message_age_seconds":0}
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events-dead/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Fri, 07 Oct 2022 20:13:36 GMT
server: uvicorn
content-length: 71
content-type: application/json

{"num_undelivered_messages":2,"oldest_unacked_message_age_seconds":573}
```

```bash
curl -i -X 'PUT' \
  'http://localhost:8000/queues/all-events-dead/redrive' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "destination_queue_id": "all-events"
}'

HTTP/1.1 204 No Content
date: Fri, 07 Oct 2022 20:16:39 GMT
server: uvicorn
content-type: application/json
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/all-events/stats' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Fri, 07 Oct 2022 20:17:09 GMT
server: uvicorn
content-length: 71
content-type: application/json

{"num_undelivered_messages":2,"oldest_unacked_message_age_seconds":787}
```

## Delay queues

Delay queues let you postpone the delivery of new messages to consumers for a number of seconds.

```bash
curl -i -X 'POST' \
  'http://localhost:8000/queues' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "delayed-events",
  "topic_id": "events",
  "ack_deadline_seconds": 30,
  "message_retention_seconds": 1209600,
  "delivery_delay_seconds": 30
}'

HTTP/1.1 201 Created
date: Sat, 19 Nov 2022 17:53:42 GMT
server: uvicorn
content-length: 291
content-type: application/json

{
  "id":"delayed-events",
  "topic_id":"events",
  "dead_queue_id":null,
  "ack_deadline_seconds":30,
  "message_retention_seconds":1209600,
  "message_filters":null,
  "message_max_deliveries":null,
  "delivery_delay_seconds":30,
  "created_at":"2022-11-19T17:53:42.858140",
  "updated_at":"2022-11-19T17:53:42.858140"
}
```

```bash
curl -i -X 'POST' \
  'http://localhost:8000/topics/events/messages' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": {"event_name": "event3", "success": true},
  "attributes": {"event_name": "event3"}
}'

HTTP/1.1 201 Created
date: Sat, 19 Nov 2022 18:02:08 GMT
server: uvicorn
content-length: 359
content-type: application/json

{
  "data":[
    {
      "id":"ed42463c-7725-4c3d-9de0-142bb0074be6",
      "queue_id":"delayed-events",
      "data":{
        "event_name":"event3",
        "success":true
      },
      "attributes":{
        "event_name":"event3"
      },
      "delivery_attempts":0,
      "expired_at":"2022-12-03T18:02:09.435449",
      "scheduled_at":"2022-11-19T18:02:39.435449",
      "created_at":"2022-11-19T18:02:09.435449",
      "updated_at":"2022-11-19T18:02:09.435449"
    }
  ]
}
```

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/delayed-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Sat, 19 Nov 2022 18:02:24 GMT
server: uvicorn
content-length: 11
content-type: application/json

{"data":[]}
```

Wait for 30 seconds and try again:

```bash
curl -i -X 'GET' \
  'http://localhost:8000/queues/delayed-events/messages' \
  -H 'accept: application/json'

HTTP/1.1 200 OK
date: Sat, 19 Nov 2022 18:02:58 GMT
server: uvicorn
content-length: 359
content-type: application/json

{
  "data":[
    {
      "id":"ed42463c-7725-4c3d-9de0-142bb0074be6",
      "queue_id":"delayed-events",
      "data":{
        "success":true,
        "event_name":"event3"
      },
      "attributes":{
        "event_name":"event3"
      },
      "delivery_attempts":1,
      "expired_at":"2022-12-03T18:02:09.435449",
      "scheduled_at":"2022-11-19T18:03:28.853622",
      "created_at":"2022-11-19T18:02:09.435449",
      "updated_at":"2022-11-19T18:02:58.853622"
    }
  ]
}
```

## Prometheus metrics

You can enable prometheus metrics using the environment variable `fastqueue_enable_prometheus_metrics='true'`.

```bash
docker run --name fastqueue-server \
    --restart unless-stopped \
    -e fastqueue_database_url='postgresql+psycopg2://fastqueue:fastqueue@localhost:5432/fastqueue' \
    -e fastqueue_server_port=8000 \
    -e fastqueue_server_num_workers=1 \
    -e fastqueue_enable_prometheus_metrics='true' \
    --network="host" \
    quay.io/allisson/fastqueue server
```

```bash
curl -i -X 'GET' 'http://localhost:8000/metrics'

HTTP/1.1 200 OK
date: Fri, 14 Oct 2022 15:58:56 GMT
server: uvicorn
content-length: 4432
content-type: text/plain; version=0.0.4; charset=utf-8

# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 427.0
python_gc_objects_collected_total{generation="1"} 198.0
python_gc_objects_collected_total{generation="2"} 16.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 241.0
python_gc_collections_total{generation="1"} 21.0
python_gc_collections_total{generation="2"} 1.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="10",patchlevel="7",version="3.10.7"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.11103744e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 7.9659008e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.66576313315e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 0.48
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 23.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1024.0
# HELP http_requests_total Total number of requests by method, status and handler.
# TYPE http_requests_total counter
# HELP http_request_size_bytes Content length of incoming requests by handler. Only value of header is respected. Otherwise ignored. No percentile calculated.
# TYPE http_request_size_bytes summary
# HELP http_response_size_bytes Content length of outgoing responses by handler. Only value of header is respected. Otherwise ignored. No percentile calculated.
# TYPE http_response_size_bytes summary
# HELP http_request_duration_highr_seconds Latency with many buckets but no API specific labels. Made for more accurate percentile calculations.
# TYPE http_request_duration_highr_seconds histogram
http_request_duration_highr_seconds_bucket{le="0.01"} 0.0
http_request_duration_highr_seconds_bucket{le="0.025"} 0.0
http_request_duration_highr_seconds_bucket{le="0.05"} 0.0
http_request_duration_highr_seconds_bucket{le="0.075"} 0.0
http_request_duration_highr_seconds_bucket{le="0.1"} 0.0
http_request_duration_highr_seconds_bucket{le="0.25"} 0.0
http_request_duration_highr_seconds_bucket{le="0.5"} 0.0
http_request_duration_highr_seconds_bucket{le="0.75"} 0.0
http_request_duration_highr_seconds_bucket{le="1.0"} 0.0
http_request_duration_highr_seconds_bucket{le="1.5"} 0.0
http_request_duration_highr_seconds_bucket{le="2.0"} 0.0
http_request_duration_highr_seconds_bucket{le="2.5"} 0.0
http_request_duration_highr_seconds_bucket{le="3.0"} 0.0
http_request_duration_highr_seconds_bucket{le="3.5"} 0.0
http_request_duration_highr_seconds_bucket{le="4.0"} 0.0
http_request_duration_highr_seconds_bucket{le="4.5"} 0.0
http_request_duration_highr_seconds_bucket{le="5.0"} 0.0
http_request_duration_highr_seconds_bucket{le="7.5"} 0.0
http_request_duration_highr_seconds_bucket{le="10.0"} 0.0
http_request_duration_highr_seconds_bucket{le="30.0"} 0.0
http_request_duration_highr_seconds_bucket{le="60.0"} 0.0
http_request_duration_highr_seconds_bucket{le="+Inf"} 0.0
http_request_duration_highr_seconds_count 0.0
http_request_duration_highr_seconds_sum 0.0
# HELP http_request_duration_highr_seconds_created Latency with many buckets but no API specific labels. Made for more accurate percentile calculations.
# TYPE http_request_duration_highr_seconds_created gauge
http_request_duration_highr_seconds_created 1.6657631341236415e+09
# HELP http_request_duration_seconds Latency with only few buckets by handler. Made to be only used if aggregation by handler is important.
# TYPE http_request_duration_seconds histogram
```
