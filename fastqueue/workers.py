from rocketry import Rocketry
from rocketry.conds import every

from fastqueue.config import settings
from fastqueue.database import SessionLocal
from fastqueue.logger import get_logger
from fastqueue.models import Queue
from fastqueue.services import QueueService

logger = get_logger(__name__)
worker = Rocketry()


@worker.task(every(f"{settings.queue_cleanup_interval_seconds} seconds"))
def queue_cleanup_task():
    logger.info("starting queue_cleanup task")

    with SessionLocal() as session:
        for result in session.query(Queue.id):
            queue_id = result[0]
            QueueService.cleanup(id=queue_id, session=session)

    logger.info("finishing queue_cleanup task")
