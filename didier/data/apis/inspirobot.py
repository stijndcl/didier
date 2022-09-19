from http import HTTPStatus

from aiohttp import ClientSession

from didier.exceptions import HTTPException

__all__ = ["get_inspirobot_quote"]


async def get_inspirobot_quote(http_session: ClientSession) -> str:
    """Get a new InspiroBot quote"""
    async with http_session.get("https://inspirobot.me/api?generate=true") as response:
        if response.status != HTTPStatus.OK:
            raise HTTPException(response.status)

        return await response.text()
