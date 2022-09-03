from datetime import datetime

from sqlalchemy.orm import sessionmaker

from fastqueue.exceptions import NotFoundError
from fastqueue.models import Topic
from fastqueue.schemas import CreateTopicSchema, TopicSchema


class TopicService:
    def create(self, data: CreateTopicSchema, session: sessionmaker) -> TopicSchema:
        topic = Topic(id=data.id, created_at=datetime.utcnow())
        session.add(topic)
        return TopicSchema(id=topic.id, created_at=topic.created_at)

    def get(self, id: str, session: sessionmaker) -> TopicSchema:
        topic = session.query(Topic).filter_by(id=id).first()
        if topic is None:
            raise NotFoundError("topic not found")
        return TopicSchema(id=topic.id, created_at=topic.created_at)

    def delete(self, id: str, session: sessionmaker) -> None:
        self.get(id, session=session)
        session.query(Topic).filter_by(id=id).delete()
