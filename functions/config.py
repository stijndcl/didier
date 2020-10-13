import json


def config(category: str, value):
    try:
        with open("files/config.json", "r") as fp:
            configFile = json.load(fp)

        configFile[category] = value

        with open("files/config.json", "w") as fp:
            json.dump(configFile, fp)

        return True
    except Exception:
        raise Exception


def get(category):
    with open("files/config.json", "r") as fp:
        configFile = json.load(fp)

    return configFile[category] if category in configFile else None
