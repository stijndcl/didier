from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple, Dict

import discord

from functions import les, eten
from functions.timeFormatters import skip_weekends, intToWeekday
from functions.stringFormatters import leading_zero as lz


restos: Dict[str, str] = {
    "ardoyen": "Ardoyen",
    "coupure": "Coupure",
    "debrug": "De Brug",
    "dunant": "Dunant",
    "heymans": "Heymans",
    "kantienberg": "Kantienberg",
    "merelbeke": "Merelbeke",
    "sterre": "Sterre"
}


@dataclass
class Menu:
    day: Optional[str] = None
    resto: str = "sterre"
    _day: datetime = field(init=False)
    _menu: Tuple[str, str, str, str] = field(init=False)

    def __post_init__(self):
        self._day = les.find_target_date(self.day if self.day else None)
        self._day = skip_weekends(self._day)
        self.day = intToWeekday(self._day.weekday())
        self._menu = eten.etenScript(self._day)

    def to_embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.blue())
        date_formatted = f"{lz(self._day.day)}/{lz(self._day.month)}/{self._day.year}"
        embed.set_author(name=f"Menu voor {self.day.lower()} {date_formatted}")
        # embed.title = f"Resto {restos[self.resto]}"

        if "gesloten" in self._menu[0].lower():
            embed.description = "Restaurant gesloten"
        else:
            embed.add_field(name="🥣 Soep:", value=self._menu[0], inline=False)
            embed.add_field(name="🍴 Hoofdgerechten:", value=self._menu[1], inline=False)

            if self._menu[2]:
                embed.add_field(name="❄️ Koud:", value=self._menu[2], inline=False)

            if self._menu[3]:
                embed.add_field(name="🥦 Groenten:", value=self._menu[3], inline=False)

        return embed
