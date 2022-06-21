import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import custom_commands as crud
from database.exceptions.constraints import DuplicateInsertException
from database.models import CustomCommand, CustomCommandAlias


async def test_create_command_non_existing(database_session: AsyncSession):
    """Test creating a new command when it doesn't exist yet"""
    await crud.create_command(database_session, "name", "response")

    commands = (await database_session.execute(select(CustomCommand))).scalars().all()
    assert len(commands) == 1
    assert commands[0].name == "name"


async def test_create_command_duplicate_name(database_session: AsyncSession):
    """Test creating a command when the name already exists"""
    await crud.create_command(database_session, "name", "response")

    with pytest.raises(DuplicateInsertException):
        await crud.create_command(database_session, "name", "other response")


async def test_create_command_name_is_alias(database_session: AsyncSession):
    """Test creating a command when the name is taken by an alias"""
    await crud.create_command(database_session, "name", "response")
    await crud.create_alias(database_session, "name", "n")

    with pytest.raises(DuplicateInsertException):
        await crud.create_command(database_session, "n", "other response")


async def test_create_alias_non_existing(database_session: AsyncSession):
    """Test creating an alias when the name is still free"""
    command = await crud.create_command(database_session, "name", "response")
    await crud.create_alias(database_session, command.name, "n")

    await database_session.refresh(command)
    assert len(command.aliases) == 1
    assert command.aliases[0].alias == "n"


async def test_create_alias_duplicate(database_session: AsyncSession):
    """Test creating an alias when another alias already has this name"""
    command = await crud.create_command(database_session, "name", "response")
    await crud.create_alias(database_session, command.name, "n")

    with pytest.raises(DuplicateInsertException):
        await crud.create_alias(database_session, command.name, "n")


async def test_create_alias_is_command(database_session: AsyncSession):
    """Test creating an alias when the name is taken by a command"""
    await crud.create_command(database_session, "n", "response")
    command = await crud.create_command(database_session, "name", "response")

    with pytest.raises(DuplicateInsertException):
        await crud.create_alias(database_session, command.name, "n")


async def test_create_alias_match_by_alias(database_session: AsyncSession):
    """Test creating an alias for a command when matching the name to another alias"""
    command = await crud.create_command(database_session, "name", "response")
    await crud.create_alias(database_session, command.name, "a1")
    alias = await crud.create_alias(database_session, "a1", "a2")
    assert alias.command == command


async def test_get_command_by_name_exists(database_session: AsyncSession):
    """Test getting a command by name"""
    await crud.create_command(database_session, "name", "response")
    command = await crud.get_command(database_session, "name")
    assert command is not None


async def test_get_command_by_cleaned_name(database_session: AsyncSession):
    """Test getting a command by the cleaned version of the name"""
    command = await crud.create_command(database_session, "CAPITALIZED NAME WITH SPACES", "response")
    found = await crud.get_command(database_session, "capitalizednamewithspaces")
    assert command == found


async def test_get_command_by_alias(database_session: AsyncSession):
    """Test getting a command by an alias"""
    command = await crud.create_command(database_session, "name", "response")
    await crud.create_alias(database_session, command.name, "a1")
    await crud.create_alias(database_session, command.name, "a2")

    found = await crud.get_command(database_session, "a1")
    assert command == found


async def test_get_command_non_existing(database_session: AsyncSession):
    """Test getting a command when it doesn't exist"""
    assert await crud.get_command(database_session, "name") is None
