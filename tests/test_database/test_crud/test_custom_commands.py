import pytest
from sqlalchemy import select

from database.crud import custom_commands as crud
from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from database.schemas.relational import CustomCommand


async def test_create_command_non_existing(postgres):
    """Test creating a new command when it doesn't exist yet"""
    await crud.create_command(postgres, "name", "response")

    commands = (await postgres.execute(select(CustomCommand))).scalars().all()
    assert len(commands) == 1
    assert commands[0].name == "name"


async def test_create_command_duplicate_name(postgres):
    """Test creating a command when the name already exists"""
    await crud.create_command(postgres, "name", "response")

    with pytest.raises(DuplicateInsertException):
        await crud.create_command(postgres, "name", "other response")


async def test_create_command_name_is_alias(postgres):
    """Test creating a command when the name is taken by an alias"""
    await crud.create_command(postgres, "name", "response")
    await crud.create_alias(postgres, "name", "n")

    with pytest.raises(DuplicateInsertException):
        await crud.create_command(postgres, "n", "other response")


async def test_create_alias(postgres):
    """Test creating an alias when the name is still free"""
    command = await crud.create_command(postgres, "name", "response")
    await crud.create_alias(postgres, command.name, "n")

    await postgres.refresh(command)
    assert len(command.aliases) == 1
    assert command.aliases[0].alias == "n"


async def test_create_alias_non_existing(postgres):
    """Test creating an alias when the command doesn't exist"""
    with pytest.raises(NoResultFoundException):
        await crud.create_alias(postgres, "name", "alias")


async def test_create_alias_duplicate(postgres):
    """Test creating an alias when another alias already has this name"""
    command = await crud.create_command(postgres, "name", "response")
    await crud.create_alias(postgres, command.name, "n")

    with pytest.raises(DuplicateInsertException):
        await crud.create_alias(postgres, command.name, "n")


async def test_create_alias_is_command(postgres):
    """Test creating an alias when the name is taken by a command"""
    await crud.create_command(postgres, "n", "response")
    command = await crud.create_command(postgres, "name", "response")

    with pytest.raises(DuplicateInsertException):
        await crud.create_alias(postgres, command.name, "n")


async def test_create_alias_match_by_alias(postgres):
    """Test creating an alias for a command when matching the name to another alias"""
    command = await crud.create_command(postgres, "name", "response")
    await crud.create_alias(postgres, command.name, "a1")
    alias = await crud.create_alias(postgres, "a1", "a2")
    assert alias.command == command


async def test_get_command_by_name_exists(postgres):
    """Test getting a command by name"""
    await crud.create_command(postgres, "name", "response")
    command = await crud.get_command(postgres, "name")
    assert command is not None


async def test_get_command_by_cleaned_name(postgres):
    """Test getting a command by the cleaned version of the name"""
    command = await crud.create_command(postgres, "CAPITALIZED NAME WITH SPACES", "response")
    found = await crud.get_command(postgres, "capitalizednamewithspaces")
    assert command == found


async def test_get_command_by_alias(postgres):
    """Test getting a command by an alias"""
    command = await crud.create_command(postgres, "name", "response")
    await crud.create_alias(postgres, command.name, "a1")
    await crud.create_alias(postgres, command.name, "a2")

    found = await crud.get_command(postgres, "a1")
    assert command == found


async def test_get_command_non_existing(postgres):
    """Test getting a command when it doesn't exist"""
    assert await crud.get_command(postgres, "name") is None


async def test_edit_command(postgres):
    """Test editing an existing command"""
    command = await crud.create_command(postgres, "name", "response")
    await crud.edit_command(postgres, command.name, "new name", "new response")
    assert command.name == "new name"
    assert command.response == "new response"


async def test_edit_command_non_existing(postgres):
    """Test editing a command that doesn't exist"""
    with pytest.raises(NoResultFoundException):
        await crud.edit_command(postgres, "name", "n", "r")
