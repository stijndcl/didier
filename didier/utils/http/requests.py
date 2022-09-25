import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from aiohttp import ClientResponse, ClientSession, ContentTypeError

from didier.exceptions.http_exception import HTTPException

logger = logging.getLogger(__name__)


__all__ = ["ensure_get", "ensure_post"]


def request_successful(response: ClientResponse) -> bool:
    """Check if a request was successful or not"""
    return 200 <= response.status < 300


@asynccontextmanager
async def ensure_get(
    http_session: ClientSession, endpoint: str, *, params: Optional[dict] = None, log_exceptions: bool = True
) -> AsyncGenerator[dict, None]:
    """Context manager that automatically raises an exception if a GET-request fails"""
    async with http_session.get(endpoint, params=params) as response:
        try:
            content = await response.json()
        except ContentTypeError:
            content = await response.text()

        if not request_successful(response):
            if log_exceptions:
                logger.error("Failed HTTP request to %s (status %s)\nResponse: %s", endpoint, response.status, content)

            raise HTTPException(response.status)

        yield await response.json()


@asynccontextmanager
async def ensure_post(
    http_session: ClientSession,
    endpoint: str,
    payload: dict,
    *,
    log_exceptions: bool = True,
    expect_return: bool = True
) -> AsyncGenerator[dict, None]:
    """Context manager that automatically raises an exception if a POST-request fails"""
    async with http_session.post(endpoint, data=payload) as response:
        if not request_successful(response):
            try:
                content = await response.json()
            except ContentTypeError:
                content = await response.text()

            if log_exceptions:
                logger.error(
                    "Failed HTTP request to %s (status %s)\nPayload: %s\nResponse: %s",
                    endpoint,
                    response.status,
                    payload,
                    content,
                )

            raise HTTPException(response.status)

        if expect_return:
            yield await response.json()
        else:
            # Always return A dict so you can always "use" the result without having to check
            # if it is None or not
            yield {}
