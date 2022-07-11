from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions.constraints import DuplicateInsertException
from database.exceptions.not_found import NoResultFoundException
from database.models import CustomCommand, CustomCommandAlias

__all__ = [
    "clean_name",
    "create_alias",
    "create_command",
    "edit_command",
    "get_command",
    "get_command_by_alias",
    "get_command_by_name",
]


def clean_name(name: str) -> str:
    """Convert a name to lowercase & remove spaces to allow easier matching"""
    return name.lower().replace(" ", "")


async def create_command(session: AsyncSession, name: str, response: str) -> CustomCommand:
    """Create a new custom command"""
    # Check if command or alias already exists
    command = await get_command(session, name)
    if command is not None:
        raise DuplicateInsertException

    command = CustomCommand(name=name, indexed_name=clean_name(name), response=response)
    session.add(command)
    await session.commit()
    return command


async def create_alias(session: AsyncSession, command: str, alias: str) -> CustomCommandAlias:
    """Create an alias for a command"""
    # Check if the command exists
    command_instance = await get_command(session, command)
    if command_instance is None:
        raise NoResultFoundException

    # Check if the alias exists (either as an alias or as a name)
    if await get_command(session, alias) is not None:
        raise DuplicateInsertException

    alias_instance = CustomCommandAlias(alias=alias, indexed_alias=clean_name(alias), command=command_instance)
    session.add(alias_instance)
    await session.commit()

    return alias_instance


async def get_command(session: AsyncSession, message: str) -> Optional[CustomCommand]:
    """Try to get a command out of a message"""
    # Search lowercase & without spaces
    message = clean_name(message)
    return (await get_command_by_name(session, message)) or (await get_command_by_alias(session, message))


async def get_command_by_name(session: AsyncSession, message: str) -> Optional[CustomCommand]:
    """Try to get a command by its name"""
    statement = select(CustomCommand).where(CustomCommand.indexed_name == message)
    return (await session.execute(statement)).scalar_one_or_none()


async def get_command_by_alias(session: AsyncSession, message: str) -> Optional[CustomCommand]:
    """Try to get a command by its alias"""
    statement = select(CustomCommandAlias).where(CustomCommandAlias.indexed_alias == message)
    alias = (await session.execute(statement)).scalar_one_or_none()
    if alias is None:
        return None

    return alias.command


async def edit_command(
    session: AsyncSession, original_name: str, new_name: Optional[str] = None, new_response: Optional[str] = None
) -> CustomCommand:
    """Edit an existing command"""
    # Check if the command exists
    command = await get_command(session, original_name)
    if command is None:
        raise NoResultFoundException

    if new_name is not None:
        command.name = new_name
    if new_response is not None:
        command.response = new_response

    session.add(command)
    await session.commit()

    return command
