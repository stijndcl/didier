from datetime import datetime
from typing import Optional, Union

from discord import app_commands
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.users import get_or_add_user
from database.schemas import CommandStats

__all__ = ["register_command_invocation"]


CommandT = Union[commands.Command, app_commands.Command, app_commands.ContextMenu]


async def register_command_invocation(
    session: AsyncSession, ctx: commands.Context, command: Optional[CommandT], timestamp: datetime
):
    """Create an entry for a command invocation"""
    if command is None:
        return

    await get_or_add_user(session, ctx.author.id)

    # Check the type of invocation
    context_menu = isinstance(command, app_commands.ContextMenu)

    # (This is a bit uglier but it accounts for hybrid commands)
    slash = isinstance(command, app_commands.Command) or (ctx.interaction is not None and not context_menu)

    stats = CommandStats(
        command=command.qualified_name.lower(),
        timestamp=timestamp,
        user_id=ctx.author.id,
        slash=slash,
        context_menu=context_menu,
    )

    session.add(stats)
    await session.commit()
