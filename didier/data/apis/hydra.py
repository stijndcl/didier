from datetime import datetime

from aiohttp import ClientSession

from didier.data.embeds.hydra import Menu
from didier.utils.http.requests import ensure_get

__all__ = ["fetch_menu"]


async def fetch_menu(http_session: ClientSession, day_dt: datetime) -> Menu:
    """Fetch the menu for a given day"""
    endpoint = f"https://hydra.ugent.be/api/2.0/resto/menu/nl/{day_dt.year}/{day_dt.month}/{day_dt.day}.json"
    async with ensure_get(http_session, endpoint, log_exceptions=False) as response:
        return Menu.parse_obj(response)
