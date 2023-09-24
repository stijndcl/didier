from aiohttp import ClientSession

from didier.data.embeds.urban_dictionary import Definition
from didier.utils.http.requests import ensure_get

__all__ = ["lookup", "PER_PAGE"]


PER_PAGE = 10


async def lookup(http_session: ClientSession, query: str) -> list[Definition]:
    """Fetch the Urban Dictionary definitions for a given word"""
    url = "https://api.urbandictionary.com/v0/define"

    async with ensure_get(http_session, url, params={"term": query}) as response:
        return list(map(Definition.model_validate, response["list"]))
