import json
from os import path


def check_all():
    files = ["deadlines", "hangman", "lastTasks", "locked", "lost", "stats", "ufora_notifications"]

    for f in files:
        if not path.isfile(path.join(f"files/{f}.json")):
            with open(f"files/{f}.json", "w+") as new_file, open(f"files/default/{f}.json", "r") as default:
                content = json.load(default)
                json.dump(content, new_file)
                print(f"Created missing file: files/{f}.json")
