import discord
from overrides import overrides
from pydantic import BaseModel, Field

from didier.data.embeds.base import EmbedPydantic

__all__ = ["CovidData"]


class _CovidNumbers(BaseModel):
    """Covid information for a country"""

    updated: int
    country: str = "Worldwide"
    cases: int
    today_cases: int = Field(alias="todayCases")
    deaths: int
    today_deaths: int = Field(alias="todayDeaths")
    recovered: int
    todayRecovered: int = Field(alias="todayRecovered")
    active: int
    tests: int


class CovidData(EmbedPydantic):
    """Covid information from two days combined into one model"""

    today: _CovidNumbers
    yesterday: _CovidNumbers

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        pass
