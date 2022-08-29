from pathlib import Path

from databases import Database

from alembic import command
from alembic.config import Config
from fastqueue.config import settings
from fastqueue.logger import get_logger

logger = get_logger(__name__)
force_rollback = True if settings.testing else False
database = Database(settings.async_database_url, force_rollback=force_rollback)


def run_migrations() -> None:
    parent_path = Path(__file__).parents[1]
    script_location = parent_path.joinpath(Path("alembic"))
    ini_location = parent_path.joinpath(Path("alembic.ini"))
    logger.info(
        "running db migrations", extra=dict(ini_location=ini_location, script_location=script_location)
    )
    alembic_cfg = Config(ini_location)
    alembic_cfg.set_main_option("script_location", str(script_location))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")
