from typing import Union

import discord

import settings

__all__ = ["NotInMainGuildException"]


class NotInMainGuildException(ValueError):
    """Exception raised when a user is not a member of the main guild"""

    def __init__(self, user: Union[discord.User, discord.Member]):
        super().__init__(
            f"User {user.display_name} (id {user.id}) "
            f"is not a member of the configured main guild (id {settings.DISCORD_MAIN_GUILD})."
        )
