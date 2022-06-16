import pytest

from alembic import command, config


@pytest.fixture(scope="session")
def tables():
    """Initialize a database before the tests, and then tear it down again
    Starts from an empty database and runs through all the migrations to check those as well
    while we're at it
    """
    alembic_config = config.Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")
