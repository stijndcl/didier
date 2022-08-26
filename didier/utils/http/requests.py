import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiohttp import ClientResponse, ClientSession

from didier.exceptions.http_exception import HTTPException

logger = logging.getLogger(__name__)


__all__ = ["ensure_get", "ensure_post"]


def request_successful(response: ClientResponse) -> bool:
    """Check if a request was successful or not"""
    return 200 <= response.status < 300


@asynccontextmanager
async def ensure_get(http_session: ClientSession, endpoint: str) -> AsyncGenerator[dict, None]:
    """Context manager that automatically raises an exception if a GET-request fails"""
    async with http_session.get(endpoint) as response:
        if not request_successful(response):
            logger.error(
                "Failed HTTP request to %s (status %s)\nResponse: %s", endpoint, response.status, await response.json()
            )

            raise HTTPException(response.status)

        yield await response.json()


@asynccontextmanager
async def ensure_post(
    http_session: ClientSession, endpoint: str, payload: dict, *, expect_return: bool = True
) -> AsyncGenerator[dict, None]:
    """Context manager that automatically raises an exception if a POST-request fails"""
    async with http_session.post(endpoint, data=payload) as response:
        if not request_successful(response):
            logger.error(
                "Failed HTTP request to %s (status %s)\nPayload: %s\nResponse: %s",
                endpoint,
                response.status,
                payload,
                await response.json(),
            )

            raise HTTPException(response.status)

        if expect_return:
            yield await response.json()
        else:
            # Always return A dict so you can always "use" the result without having to check
            # if it is None or not
            yield {}
