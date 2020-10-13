import random

from data import constants


def control(message):
    if str(message.author.id) == constants.didierId:
        return ""
    elif didier(message.content):
        return "Hmm?"
    elif any(term in message.content for term in ["gib dink", "gib donk"]):
        return "No."
    elif didier(message.content.split(" ")[0]) and any(term in message.content.lower() for term in ["are you sure", "are u sure"]):
        return "I'm not just sure, I'm HIV Positive."
    elif any(message.content.lower().startswith(term) for term in ["is this", "isthis", "isdis", "is dis"]):
        res = random.randint(0, 100)
        return "No, this is Patrick." if res > 90 else ""
    elif " 69" in message.content or "69 " in message.content:
        res = random.randint(0, 100)
        return "Nice." if res > 70 else ""
    elif message.content.lower() == "hey":
        res = random.randint(0, 100)
        return "You're finally awake!" if res > 90 else ""
    return ""


def didier(message):
    ml = message.lower()
    return ml == "didier" or ml == "<@!{}>".format(constants.didierId)
