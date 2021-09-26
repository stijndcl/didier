from datetime import datetime
from typing import Dict

import requests


def get_type(menu: Dict, type_: str) -> str:
    acc = ""

    for m in menu["meals"]:
        # API sometimes has empty results, also filter out wrong type
        if not m["name"] or m["type"] != type_:
            continue

        if m["kind"] == "meat":
            acc += ("* Vlees: {} ({})\n".format(m["name"], m["price"]))
        elif m["kind"] == "fish":
            acc += ("* Vis: {} ({})\n".format(m["name"], m["price"]))
        elif m["kind"] == "vegetarian":
            acc += ("* Vegetarisch: {} ({})\n".format(m["name"], m["price"]))
        elif m["kind"] == "vegan":
            acc += ("* Vegan: {} ({})\n".format(m["name"], m["price"]))

    return acc


def etenScript(dag: datetime, resto: str = "sterre"):
    # What day
    menuSoep = ""
    menuHoofdgerechten = ""
    menuKoud = ""
    menuGroenten = ""

    # Fetch from API
    try:
        menu = requests.get(f"https://zeus.ugent.be/hydra/api/2.0/resto/menu/nl-{resto}/{dag.year}/{dag.month}/{dag.day}.json").json()

        if not menu["meals"]:
            raise Exception()

        # Print menu

        for s in menu["meals"]:
            if s["kind"] == "soup":
                menuSoep += ("* {} ({})\n".format(s["name"], s["price"]))

        menuHoofdgerechten = get_type(menu, "main")
        menuKoud = get_type(menu, "cold")

        for v in menu["vegetables"]:
            menuGroenten += ("* {}\n".format(v))
    except Exception:
        menuSoep += "Restaurant gesloten"
        menuGroenten += "Restaurant gesloten"
        menuHoofdgerechten += "Restaurant gesloten"
        menuKoud += "Restaurant gesloten"
    return menuSoep, menuHoofdgerechten, menuKoud, menuGroenten
