from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType
from functions import config, checks
from functions.football import get_matches, get_table, get_jpl_code
from startup.didier import Didier


class FootballSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="jpl", description="Jupiler Pro League commands")
    async def _jpl_group(self, interaction: SlashInteraction):
        pass

    @_jpl_group.sub_command(name="matches",
                            description="Schema voor een bepaalde speeldag",
                            options=[
                                Option("day", "Speeldag (default huidige)", OptionType.INTEGER)
                            ]
                            )
    async def _jpl_matches_slash(self, interaction: SlashInteraction, day: int = None):
        # Default is current day
        if day is None:
            day = int(config.get("jpl_day"))

        await interaction.reply(get_matches(day))

    @_jpl_group.sub_command(name="table", description="Huidige rangschikking")
    async def _jpl_table_slash(self, interaction: SlashInteraction):
        await interaction.reply(get_table())

    @_jpl_group.sub_command(name="update", description="Update de code voor deze competitie (owner-only)")
    async def _jpl_update_slash(self, interaction: SlashInteraction):
        if not await checks.isMe(interaction):
            return await interaction.reply(f"Je hebt geen toegang tot dit commando.")

        code = get_jpl_code()
        config.config("jpl", code)
        await interaction.reply(f"Done (code: {code})")


def setup(client: Didier):
    client.add_cog(FootballSlash(client))
