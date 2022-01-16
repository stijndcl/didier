import datetime
import json

from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType, check
from functions.checks import isMe
from functions.timeFormatters import fromString
from startup.didier import Didier


class DBSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="db")
    @check(isMe)
    async def _db_slash(self, interaction: SlashInteraction):
        pass

    @_db_slash.sub_command_group(name="add")
    async def _add_slash(self, interaction: SlashInteraction):
        pass

    @_add_slash.sub_command(
        name="deadline",
        options=[
            Option(
                "year",
                description="Year (1-based)",
                type=OptionType.INTEGER,
                required=True
            ),
            Option(
              "course",
              description="Course (abbreviated)",
              type=OptionType.STRING,
              required=True
            ),
            Option(
              "name",
              description="Name of the deadline/project",
              type=OptionType.STRING,
              required=True
            ),
            Option(
                "date",
                description="Date (DD/MM)",
                type=OptionType.STRING,
                required=True
            ),
            Option(
                "time",
                description="Timestamp (HH:MM or HH:MM:SS)",
                type=OptionType.STRING,
                required=False
            )
        ]
    )
    async def _add_deadline_slash(self, interaction: SlashInteraction, year: int, course: str, name: str, date: str, time: str = "00:00:00"):
        with open("files/deadlines.json", "r") as f:
            deadlines = json.load(f)

        date += "/" + str(datetime.datetime.now().year)

        # Fix format
        if time.count(":") == 1:
            time += ":00"

        dt = fromString(f"{date} {time}", formatString="%d/%m/%Y %H:%M:%S", tzinfo=None)

        # Add year & course if necessary
        if str(year) not in deadlines:
            deadlines[str(year)] = {}

        if course not in deadlines[str(year)]:
            deadlines[str(year)][course] = {}

        deadlines[str(year)][course][name] = round(dt.timestamp())

        with open("files/deadlines.json", "w") as f:
            json.dump(deadlines, f)

        await interaction.reply("Addition successful", ephemeral=True)


def setup(client: Didier):
    client.add_cog(DBSlash(client))
