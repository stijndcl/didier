import discord
from overrides import overrides
from pydantic import BaseModel, Field, validator

from didier.data.embeds.base import EmbedPydantic

__all__ = ["CovidData"]


class _CovidNumbers(BaseModel):
    """Covid numbers for a country

    For worldwide numbers, country_info will be None
    """

    updated: int
    country: str = "Worldwide"
    cases: int
    today_cases: int = Field(alias="todayCases")
    deaths: int
    today_deaths: int = Field(alias="todayDeaths")
    recovered: int
    today_recovered: int = Field(alias="todayRecovered")
    active: int
    tests: int

    @validator("updated")
    def updated_to_seconds(cls, value: int) -> int:
        """Turn the updated field into seconds instead of milliseconds"""
        return int(value) // 1000


class CovidData(EmbedPydantic):
    """Covid information from two days combined into one model"""

    today: _CovidNumbers
    yesterday: _CovidNumbers

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.red(), title=f"Coronatracker {self.today.country}")
        embed.description = f"Last update: <t:{self.today.updated}:R>"
        embed.set_thumbnail(url="https://i.imgur.com/aWnDuBt.png")

        cases_indicator = self._trend_indicator(self.today.today_cases, self.yesterday.today_cases)
        embed.add_field(
            name="Cases (Today)",
            value=f"{self.today.cases:,} **({self.today.today_cases:,})** {cases_indicator}".replace(",", "."),
            inline=False,
        )

        active_indicator = self._trend_indicator(self.today.active, self.yesterday.active)
        active_diff = self.today.active - self.yesterday.active
        embed.add_field(
            name="Active (Today)",
            value=f"{self.today.active:,} **({self._with_sign(active_diff)})** {active_indicator}".replace(",", "."),
            inline=False,
        )

        deaths_indicator = self._trend_indicator(self.today.today_deaths, self.yesterday.today_deaths)
        embed.add_field(
            name="Deaths (Today)",
            value=f"{self.today.deaths:,} **({self.today.today_deaths:,})** {deaths_indicator}".replace(",", "."),
            inline=False,
        )

        recovered_indicator = self._trend_indicator(self.today.today_recovered, self.yesterday.today_recovered)
        embed.add_field(
            name="Recovered (Today)",
            value=f"{self.today.recovered} **({self.today.today_recovered:,})** {recovered_indicator}".replace(
                ",", "."
            ),
            inline=False,
        )

        tests_diff = self.today.tests - self.yesterday.tests
        embed.add_field(
            name="Tests Administered (Today)",
            value=f"{self.today.tests:,} **({tests_diff:,})**".replace(",", "."),
            inline=False,
        )

        return embed

    def _with_sign(self, value: int) -> str:
        """Prepend a + symbol if a number is positive"""
        if value > 0:
            return f"+{value:,}"

        return f"{value:,}"

    def _trend_indicator(self, today: int, yesterday: int) -> str:
        """Function that returns a rise/decline indicator for the target key."""
        if today > yesterday:
            return ":small_red_triangle:"

        if yesterday > today:
            return ":small_red_triangle_down:"

        return ""
