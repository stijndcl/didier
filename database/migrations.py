import logging

from sqlalchemy.orm import Session

from alembic import command, script
from alembic.config import Config
from alembic.runtime import migration
from database.engine import postgres_engine

__config_path__ = "alembic.ini"
__migrations_path__ = "alembic/"


cfg = Config(__config_path__)
cfg.set_main_option("script_location", __migrations_path__)


__all__ = ["ensure_latest_migration", "migrate"]


async def ensure_latest_migration():
    """Make sure we are currently on the latest revision, otherwise raise an exception"""
    alembic_script = script.ScriptDirectory.from_config(cfg)

    async with postgres_engine.begin() as connection:
        current_revision = await connection.run_sync(
            lambda sync_connection: migration.MigrationContext.configure(sync_connection).get_current_revision()
        )

        alembic_head = alembic_script.get_current_head()

        if current_revision != alembic_head:
            error_message = (
                f"Pending migrations (current revision is {current_revision}, while head is at {alembic_head})"
            )
            logging.error(error_message)
            raise RuntimeError(error_message)


def __execute_upgrade(connection: Session):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


def __execute_downgrade(connection: Session):
    cfg.attributes["connection"] = connection
    command.downgrade(cfg, "base")


async def migrate(up: bool):
    """Migrate the database upwards or downwards"""
    async with postgres_engine.begin() as connection:
        await connection.run_sync(__execute_upgrade if up else __execute_downgrade)
