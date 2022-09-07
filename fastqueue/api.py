import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from fastqueue.config import settings
from fastqueue.database import SessionLocal
from fastqueue.exceptions import AlreadyExistsError, NotFoundError
from fastqueue.schemas import CreateQueueSchema, CreateTopicSchema, ListTopicSchema, QueueSchema, TopicSchema
from fastqueue.services import QueueService, TopicService

app = FastAPI(debug=settings.debug)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/topics", response_model=TopicSchema, status_code=status.HTTP_201_CREATED)
def create_topic(data: CreateTopicSchema, session: Session = Depends(get_session)):
    try:
        return TopicService.create(data=data, session=session)
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.args[0])


@app.get("/topics/{topic_id}", response_model=TopicSchema, status_code=status.HTTP_200_OK)
def get_topic(topic_id: str, session: Session = Depends(get_session)):
    try:
        return TopicService.get(id=topic_id, session=session)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0])


@app.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: str, session: Session = Depends(get_session)):
    try:
        return TopicService.delete(id=topic_id, session=session)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0])


@app.get("/topics", response_model=ListTopicSchema, status_code=status.HTTP_200_OK)
def list_topics(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return TopicService.list(filters=None, offset=offset, limit=limit, session=session)


@app.post("/queues", response_model=QueueSchema, status_code=status.HTTP_201_CREATED)
def create_queue(data: CreateQueueSchema, session: Session = Depends(get_session)):
    try:
        return QueueService.create(data=data, session=session)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0])
    except AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.args[0])


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
