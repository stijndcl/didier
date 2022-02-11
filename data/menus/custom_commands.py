from typing import Union

from discord import ApplicationContext
from discord.ext.commands import Context

from data.menus.paginated import Paginated
from functions.database.custom_commands import get_all
from functions.stringFormatters import capitalize


class CommandsList(Paginated):
    def __init__(self, ctx: Union[ApplicationContext, Context]):
        all_commands = get_all()
        commands_sorted = list(sorted(map(lambda x: (capitalize(x["name"]),), all_commands)))
        super().__init__(ctx=ctx, title="Custom Commands", data=commands_sorted, per_page=15)

    def format_entry(self, index: int, value: tuple) -> str:
        return value[0]
