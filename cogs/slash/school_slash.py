from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option, AutocompleteContext

from data import schedule
from data.courses import load_courses, find_course_from_name
from data.embeds.food import Menu
from data.embeds.deadlines import Deadlines
from functions import les, config
from functions.stringFormatters import capitalize
from functions.timeFormatters import skip_weekends
from startup.didier import Didier


# Preload autocomplete constants to allow for smoother results
courses = load_courses()
days = ["Morgen", "Overmorgen", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]


def day_autocomplete(ctx: AutocompleteContext) -> list[str]:
    return [day for day in days if day.lower().startswith(ctx.value.lower())]


def course_autocomplete(ctx: AutocompleteContext) -> list[str]:
    return [course for course in courses if course.lower().startswith(ctx.value.lower())]


class SchoolSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="eten", description="Menu in de UGent resto's op een bepaalde dag")
    async def _food_slash(self, ctx: ApplicationContext,
                          dag: Option(str, description="Dag", required=False, default=None, autocomplete=day_autocomplete)
                          ):
        embed = Menu(dag).to_embed()
        await ctx.respond(embed=embed)

    @slash_command(name="deadlines", description="Aanstaande deadlines")
    async def _deadlines_slash(self, ctx: ApplicationContext):
        embed = Deadlines().to_embed()
        await ctx.respond(embed=embed)

    @slash_command(name="les", description="Lessenrooster voor [Dag] (default vandaag)",)
    async def _schedule_slash(self, ctx: ApplicationContext,
                              dag: Option(str, description="Dag", required=False, default=None, autocomplete=day_autocomplete)
                              ):
        """It's late and I really don't want to refactor the original right now"""
        if dag is not None:
            dag = dag.lower()

        date = les.find_target_date(dag)

        # Person explicitly requested a weekend-day
        if dag is not None and dag.lower() in ("morgen", "overmorgen") and date.weekday() > 4:
            return await ctx.respond(f"{capitalize(dag)} is het weekend.", ephemeral=True)

        date = skip_weekends(date)

        s = schedule.Schedule(date, int(config.get("year")), int(config.get("semester")), dag is not None)

        if s.semester_over:
            return await ctx.respond("Het semester is afgelopen.", ephemeral=True)

        # DM only shows user's own minor
        if ctx.guild is None:
            minor_roles = [*schedule.find_minor(self.client, ctx.interaction.user.id)]
            return await ctx.respond(embed=s.create_schedule(minor_roles=minor_roles).to_embed())

        return await ctx.respond(embed=s.create_schedule().to_embed())

    @slash_command(name="fiche", description="Zoek de studiefiche voor een vak.")
    async def _study_guide_slash(self, ctx: ApplicationContext,
                                 vak: Option(str, description="Naam van het vak. Afkortingen werken ook, maar worden niet ge-autocompletet.",
                                             required=True, autocomplete=course_autocomplete)):
        # Find code corresponding to the search query
        course = find_course_from_name(vak, courses)

        # Code not found
        if course is None:
            return await ctx.respond(f"Onbekend vak: \"{vak}\".", ephemeral=True)

        # Get the guide for the current year
        year = 2018 + int(config.get("year"))
        return await ctx.respond(f"https://studiekiezer.ugent.be/studiefiche/nl/{course.code}/{year}")


def setup(client: Didier):
    client.add_cog(SchoolSlash(client))
