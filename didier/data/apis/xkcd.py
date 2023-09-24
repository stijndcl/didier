from typing import Optional

from aiohttp import ClientSession

from didier.data.embeds.xkcd import XKCDPost
from didier.utils.http.requests import ensure_get

__all__ = ["fetch_xkcd_post"]


async def fetch_xkcd_post(http_session: ClientSession, *, num: Optional[int] = None) -> XKCDPost:
    """Fetch a post from xkcd.com"""
    url = "https://xkcd.com" + (f"/{num}" if num is not None else "") + "/info.0.json"

    async with ensure_get(http_session, url) as response:
        return XKCDPost.model_validate(response)
