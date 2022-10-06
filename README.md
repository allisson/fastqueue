# fastqueue
Simple queue system based on FastAPI and PostgreSQL.

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
