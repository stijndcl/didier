import os

import requests

from functions.database.memes import Meme
from functions.mock import mock


def generate(meme: Meme, fields):
    """
    Main function that takes a Meme as input & generates an image.
    """
    # If there's only one field, the user isn't required to use quotes
    if meme.fields == 1:
        fields = [" ".join(fields)]

    fields = _apply_meme(meme, fields)

    # List of fields to send to the API
    boxes = [{"text": ""}, {"text": ""}, {"text": ""}, {"text": ""}]

    # Add all fields required & ignore the excess ones
    for i in range(len(fields)):
        if i > 3:
            break
        boxes[i]["text"] = fields[i]

    # Check server status
    req = requests.get('https://api.imgflip.com/get_memes').json()

    # Server is down
    if not req["success"]:
        return {"success": False, "message": "Er is een fout opgetreden."}

    # Post meme
    reply = _post_meme(meme, boxes)

    # Adding a message parameter makes the code in the cog a lot cleaner
    if not reply["success"]:
        reply["message"] = "Error! Controleer of je de juiste syntax hebt gebruikt. Gebruik het commando " \
                           "\"memes\" voor een lijst aan geaccepteerde meme-namen."
    else:
        reply["message"] = reply["data"]["url"]

    return reply


def _post_meme(meme: Meme, boxes):
    """
    Performs API request to generate the meme
    """
    caption = {
        "template_id": meme.meme_id,
        "username": os.getenv("IMGFLIPNAME"),
        "password": os.getenv("IMGFLIPPASSWORD"),
        "boxes[0][text]": boxes[0]["text"],
        "boxes[1][text]": boxes[1]["text"],
        "boxes[2][text]": boxes[2]["text"],
        "boxes[3][text]": boxes[3]["text"]
    }

    # Send the POST to the API
    memeReply = requests.post('https://api.imgflip.com/caption_image', caption).json()

    return memeReply


def _apply_meme(meme: Meme, fields):
    """
    Some memes are in a special format that only requires
    a few words to be added, or needs the input to be changed.
    This function handles all that.

    Links certain meme id's to functions that need to be applied first.
    """
    memeDict = {
        102156234: mocking_spongebob,
        91538330: _x_x_everywhere,
        252600902: _always_has_been,
        167754325: _math_is_math
    }

    # Meme needs no special treatment
    if meme.meme_id not in memeDict:
        return fields

    return memeDict[meme.meme_id](fields)


def mocking_spongebob(fields):
    return list(map(mock, fields))


def _x_x_everywhere(fields):
    word = fields[0]

    return ["{}".format(word), "{} everywhere".format(word)]


def _always_has_been(fields):
    word = fields[0]

    return ["Wait, {}?".format(word), "Always has been"]


def _math_is_math(fields):
    word = fields[0]

    return [f"{word.upper()} IS {word.upper()}!"]
