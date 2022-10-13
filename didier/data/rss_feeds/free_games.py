import logging
from http import HTTPStatus

import feedparser
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.free_games import add_free_games, filter_present_games
from didier.data.embeds.free_games import SEPARATOR, FreeGameEmbed

logger = logging.getLogger(__name__)


__all__ = ["fetch_free_games"]


async def fetch_free_games(http_session: ClientSession, database_session: AsyncSession) -> list[FreeGameEmbed]:
    """Get a fresh list of free games"""
    url = "https://pepeizqdeals.com/?call_custom_simple_rss=1&csrp_cat=12"
    async with http_session.get(url) as response:
        if response.status != HTTPStatus.OK:
            logger.error("Free games GET-request failed with status code %d." % response.status)
            return []

        feed = feedparser.parse(await response.text())

    games: list[FreeGameEmbed] = []
    game_ids: list[int] = []

    for entry in feed["entries"]:
        # Game isn't free
        if SEPARATOR not in entry["title"]:
            continue

        game = FreeGameEmbed.parse_obj(entry)
        games.append(game)
        game_ids.append(game.dc_identifier)

    # Filter out games that we already know
    filtered_ids = await filter_present_games(database_session, game_ids)

    # Insert new games into the database
    await add_free_games(database_session, filtered_ids)

    return list(filter(lambda x: x.dc_identifier in filtered_ids, games))
