from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType

from data import schedule
from data.embeds.food import Menu
from data.embeds.deadlines import Deadlines
from functions import les, config
from functions.stringFormatters import capitalize
from functions.timeFormatters import skip_weekends
from startup.didier import Didier


class SchoolSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(
        name="eten",
        description="Menu in de UGENT resto's op een bepaalde dag",
        options=[
            Option(
                "dag",
                description="Dag",
                type=OptionType.STRING
            )
        ]
    )
    async def _food_slash(self, interaction: SlashInteraction, dag: str = None):
        embed = Menu(dag).to_embed()
        await interaction.reply(embed=embed)

    @slash_command(name="deadlines", description="Aanstaande deadlines")
    async def _deadlines_slash(self, interaction: SlashInteraction):
        embed = Deadlines().to_embed()
        await interaction.reply(embed=embed)

    @slash_command(
        name="les",
        description="Lessenrooster voor [Dag] (default vandaag)",
        options=[
            Option(
                "dag",
                description="dag",
                type=OptionType.STRING,
                required=False
            )
        ]
    )
    async def _schedule_slash(self, interaction: SlashInteraction, day: str = None):
        """It's late and I really don't want to refactor the original right now"""
        if day is not None:
            day = day.lower()

        date = les.find_target_date(day)

        # Person explicitly requested a weekend-day
        if day is not None and day.lower() in ("morgen", "overmorgen") and date.weekday() > 4:
            return await interaction.reply(f"{capitalize(day)} is het weekend.", ephemeral=True)

        date = skip_weekends(date)

        s = schedule.Schedule(date, int(config.get("year")), int(config.get("semester")), day is not None)

        if s.semester_over:
            return await interaction.reply("Het semester is afgelopen.", ephemeral=True)

        # DM only shows user's own minor
        if interaction.guild is None:
            minor_roles = [*schedule.find_minor(self.client, interaction.author.id)]
            return await interaction.reply(embed=s.create_schedule(minor_roles=minor_roles).to_embed())

        return await interaction.reply(embed=s.create_schedule().to_embed())


def setup(client: Didier):
    client.add_cog(SchoolSlash(client))
