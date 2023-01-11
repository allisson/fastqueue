import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from fastqueue.config import settings
from fastqueue.database import SessionLocal
from fastqueue.exceptions import AlreadyExistsError, NotFoundError
from fastqueue.schemas import (
    CreateMessageSchema,
    CreateQueueSchema,
    CreateTopicSchema,
    ListMessageSchema,
    ListQueueSchema,
    ListTopicSchema,
    NotFoundSchema,
    QueueSchema,
    QueueStatsSchema,
    RedriveQueueSchema,
    TopicSchema,
    UpdateQueueSchema,
)
from fastqueue.services import MessageService, QueueService, TopicService

tags_metadata = [
    {
        "name": "topics",
        "description": "Operations with topics.",
    },
    {
        "name": "queues",
        "description": "Operations with queues.",
    },
    {
        "name": "messages",
        "description": "Operations with messages.",
    },
]
app = FastAPI(
    title="fastqueue",
    description="Simple queue system based on FastAPI and PostgreSQL.",
    debug=settings.debug,
    openapi_tags=tags_metadata,
)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    if not settings.enable_prometheus_metrics:
        return
    Instrumentator().instrument(app).expose(app)


@app.exception_handler(AlreadyExistsError)
def already_exists_exception_handler(request: Request, exc: AlreadyExistsError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.args[0]})


@app.exception_handler(NotFoundError)
def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.args[0]})


@app.post("/topics", response_model=TopicSchema, status_code=status.HTTP_201_CREATED, tags=["topics"])
def create_topic(data: CreateTopicSchema, session: Session = Depends(get_session)):
    return TopicService(session=session).create(data=data)


@app.get(
    "/topics/{topic_id}",
    response_model=TopicSchema,
    status_code=status.HTTP_200_OK,
    tags=["topics"],
    responses={404: {"model": NotFoundSchema}},
)
def get_topic(topic_id: str, session: Session = Depends(get_session)):
    return TopicService(session=session).get(id=topic_id)


@app.delete(
    "/topics/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["topics"],
    responses={404: {"model": NotFoundSchema}},
)
def delete_topic(topic_id: str, session: Session = Depends(get_session)):
    return TopicService(session=session).delete(id=topic_id)


@app.get("/topics", response_model=ListTopicSchema, status_code=status.HTTP_200_OK, tags=["topics"])
def list_topics(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return TopicService(session=session).list(filters=None, offset=offset, limit=limit)


@app.post("/queues", response_model=QueueSchema, status_code=status.HTTP_201_CREATED, tags=["queues"])
def create_queue(data: CreateQueueSchema, session: Session = Depends(get_session)):
    return QueueService(session=session).create(data=data)


@app.get(
    "/queues/{queue_id}",
    response_model=QueueSchema,
    status_code=status.HTTP_200_OK,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def get_queue(queue_id: str, session: Session = Depends(get_session)):
    return QueueService(session=session).get(id=queue_id)


@app.put(
    "/queues/{queue_id}",
    response_model=QueueSchema,
    status_code=status.HTTP_200_OK,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def update_queue(queue_id: str, data: UpdateQueueSchema, session: Session = Depends(get_session)):
    return QueueService(session=session).update(id=queue_id, data=data)


@app.get(
    "/queues/{queue_id}/stats",
    response_model=QueueStatsSchema,
    status_code=status.HTTP_200_OK,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def get_queue_stats(queue_id: str, session: Session = Depends(get_session)):
    return QueueService(session=session).stats(id=queue_id)


@app.put(
    "/queues/{queue_id}/purge",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def purge_queue_messages(queue_id: str, session: Session = Depends(get_session)):
    return QueueService(session=session).purge(id=queue_id)


@app.put(
    "/queues/{queue_id}/redrive",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def redrive_queue_messages(queue_id: str, data: RedriveQueueSchema, session: Session = Depends(get_session)):
    return QueueService(session=session).redrive(id=queue_id, data=data)


@app.delete(
    "/queues/{queue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["queues"],
    responses={404: {"model": NotFoundSchema}},
)
def delete_queue(queue_id: str, session: Session = Depends(get_session)):
    return QueueService(session=session).delete(id=queue_id)


@app.get("/queues", response_model=ListQueueSchema, status_code=status.HTTP_200_OK, tags=["queues"])
def list_queues(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return QueueService(session=session).list(filters=None, offset=offset, limit=limit)


@app.post(
    "/topics/{topic_id}/messages",
    response_model=ListMessageSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["messages"],
    responses={404: {"model": NotFoundSchema}},
)
def create_message(topic_id: str, data: CreateMessageSchema, session: Session = Depends(get_session)):
    return MessageService(session=session).create(topic_id=topic_id, data=data)


@app.get(
    "/queues/{queue_id}/messages",
    response_model=ListMessageSchema,
    status_code=status.HTTP_200_OK,
    tags=["messages"],
    responses={404: {"model": NotFoundSchema}},
)
def list_messages_for_consume(queue_id: str, limit: int = 10, session: Session = Depends(get_session)):
    return MessageService(session=session).list_for_consume(queue_id=queue_id, limit=limit)


@app.put("/messages/{message_id}/ack", status_code=status.HTTP_204_NO_CONTENT, tags=["messages"])
def ack_message(message_id: str, session: Session = Depends(get_session)):
    return MessageService(session=session).ack(id=message_id)


@app.put("/messages/{message_id}/nack", status_code=status.HTTP_204_NO_CONTENT, tags=["messages"])
def nack_message(message_id: str, session: Session = Depends(get_session)):
    return MessageService(session=session).nack(id=message_id)


def run_server():
    uvicorn.run(
        "fastqueue.api:app",
        debug=settings.debug,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
        reload=settings.server_reload,
        workers=settings.server_num_workers,
    )
