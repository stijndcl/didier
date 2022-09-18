from typing import Union

import discord

from didier import Didier
from didier.exceptions import NotInMainGuildException

__all__ = ["to_main_guild_member"]


def to_main_guild_member(client: Didier, user: Union[discord.User, discord.Member]) -> discord.Member:
    """Turn a discord.User into a discord.Member instance

    This assumes the user is in CoC. If not, it raises a NotInMainGuildException
    """
    main_guild = client.main_guild

    # Already a discord.Member instance
    if isinstance(user, discord.Member) and user.guild == main_guild:
        return user

    member = main_guild.get_member(user.id)
    if member is None:
        raise NotInMainGuildException(user)

    return member
