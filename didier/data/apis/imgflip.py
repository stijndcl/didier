from aiohttp import ClientSession

import settings
from database.schemas import MemeTemplate
from didier.exceptions.missing_env import MissingEnvironmentVariable
from didier.utils.http.requests import ensure_post

__all__ = ["generate_meme"]


def generate_boxes(meme: MemeTemplate, fields: list[str]) -> list[str]:
    """Generate the template boxes for Imgflip"""
    # If no fields were passed, generate a template instead
    if not fields:
        fields = [f"Field #{i + 1}" for i in range(meme.field_count)]

    # If a meme only has 1 field, join all the arguments together into one string
    if meme.field_count == 1:
        fields = [" ".join(fields)]

    fields = fields[: min(20, meme.field_count)]
    # TODO manipulate the text if necessary
    return fields


async def generate_meme(http_session: ClientSession, meme: MemeTemplate, fields: list[str]) -> str:
    """Make a request to Imgflip to generate a meme"""
    name, password = settings.IMGFLIP_NAME, settings.IMGFLIP_PASSWORD

    # Ensure credentials exist
    if name is None:
        raise MissingEnvironmentVariable("IMGFLIP_NAME")

    if password is None:
        raise MissingEnvironmentVariable("IMGFLIP_PASSWORD")

    boxes = generate_boxes(meme, fields)
    payload = {"template_id": meme.template_id, "username": name, "password": password}
    for i, box in enumerate(boxes):
        payload[f"boxes[{i}][text]"] = box

    async with ensure_post(http_session, "https://api.imgflip.com/caption_image", payload=payload) as response:
        return response["data"]["url"]
