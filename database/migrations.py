import logging

from alembic import config, script
from alembic.runtime import migration

from database.engine import engine


async def ensure_latest_migration():
    """Make sure we are currently on the latest revision, otherwise raise an exception"""
    alembic_config = config.Config("alembic.ini")
    alembic_script = script.ScriptDirectory.from_config(alembic_config)

    async with engine.begin() as connection:
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
