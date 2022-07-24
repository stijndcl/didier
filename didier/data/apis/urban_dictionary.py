from http import HTTPStatus

from aiohttp import ClientSession

from didier.data.embeds.urban_dictionary import Definition

__all__ = ["lookup", "PER_PAGE"]


PER_PAGE = 10


async def lookup(http_session: ClientSession, query: str) -> tuple[int, list[Definition]]:
    """Fetch the Urban Dictionary definitions for a given word"""
    url = "https://api.urbandictionary.com/v0/define"

    async with http_session.get(url, params={"term": query}) as response:
        if response.status != HTTPStatus.OK:
            return response.status, []

        response_json = await response.json()
        return 200, list(map(Definition.parse_obj, response_json["list"]))
