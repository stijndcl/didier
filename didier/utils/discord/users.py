from typing import Union

import discord

from database.schemas import UforaCourse
from didier import Didier
from didier.exceptions import NotInMainGuildException

__all__ = ["has_course", "to_main_guild_member"]


def has_course(member: discord.Member, course: UforaCourse) -> bool:
    """Check if a member is taking a Ufora course"""
    for role in member.roles:
        if role.id == course.role_id:
            return True

        if course.overarching_role_id is not None and course.overarching_role_id == role.id:
            return True

        if course.alternative_overarching_role_id is not None and course.alternative_overarching_role_id == role.id:
            return True

    return False


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
