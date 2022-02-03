from discord.ext import commands
from discord.commands import Option, SlashCommandGroup, ApplicationContext, permissions
from functions import config
from functions.football import get_matches, get_table, get_jpl_code
from startup.didier import Didier


class FootballSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    _jpl_group = SlashCommandGroup("jpl", "Jupiler Pro League commands")

    @_jpl_group.command(name="matches", description="Schema voor een bepaalde speeldag")
    async def _jpl_matches_slash(self, ctx: ApplicationContext,
                                 day: Option(int, name="day", description="Speeldag (default huidige)", required=False, default=None)
                                 ):
        # Default is current day
        if day is None:
            day = int(config.get("jpl_day"))

        await ctx.respond(get_matches(day))

    @_jpl_group.command(name="table", description="Huidige rangschikking")
    async def _jpl_table_slash(self, ctx: ApplicationContext):
        await ctx.respond(get_table())

    @_jpl_group.command(name="update", description="Update de code voor deze competitie (owner-only)", default_permission=False)
    @permissions.is_owner()
    async def _jpl_update_slash(self, ctx: ApplicationContext):
        code = get_jpl_code()
        config.config("jpl", code)
        await ctx.respond(f"Done (code: {code})")


def setup(client: Didier):
    client.add_cog(FootballSlash(client))
