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

    fields = _applyMeme(meme, fields)

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
    reply = _postMeme(meme, boxes)

    # Adding a message parameter makes the code in the cog a lot cleaner
    if not reply["success"]:
        reply["message"] = "Error! Controleer of je de juiste syntax hebt gebruikt. Gebruik het commando " \
                           "\"memes\" voor een lijst aan geaccepteerde meme-namen."
    else:
        reply["message"] = reply["data"]["url"]

    return reply


def _postMeme(meme: Meme, boxes):
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


def _applyMeme(meme: Meme, fields):
    """
    Some memes are in a special format that only requires
    a few words to be added, or needs the input to be changed.
    This function handles all that.

    Callbacks contains a function that modifies the input
    """
    memeDict = {
        102156234: _mockingSpongebob,
        91538330: _xXEverywhere,
        252600902: _alwaysHasBeen
    }

    # Meme needs no special treatment
    if meme.meme_id not in memeDict:
        return fields

    return memeDict[meme.meme_id](fields)


def _mockingSpongebob(fields):
    for i, field in enumerate(fields):
        fields[i] = mock(field)

    return fields


def _xXEverywhere(fields):
    word = fields[0]

    return ["{}".format(word), "{} everywhere".format(word)]


def _alwaysHasBeen(fields):
    word = fields[0]

    return ["Wait, it's all {}?".format(word), "Always has been"]
