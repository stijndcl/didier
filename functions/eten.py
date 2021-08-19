#!/usr/bin/env python3

import datetime
import requests
import sys


def etenScript(weekDag):
    # What day
    weekdagen = ('ma', 'di', 'wo', 'do', 'vr', 'za', 'zo')
    deltas = {'morgen': 1,
              'overmorgen': 2,
              'volgende': 7}

    d = datetime.date.today()

    if weekDag in deltas:
        d += datetime.timedelta(deltas[weekDag])
    if weekDag[0:2] in weekdagen:
        while d.weekday() != weekdagen.index(weekDag[0:2]):
            d += datetime.timedelta(1)

    menuSoep = ""
    menuHoofdgerechten = ""
    menuGroenten = ""

    # Fetch from API
    try:
        menu = requests.get(f"https://zeus.ugent.be/hydra/api/2.0/resto/menu/nl-sterre/{d.year}/{d.month}/{d.day}.json").json()

        if not menu["meals"]:
            raise Exception()

        # Print menu

        for s in menu["meals"]:
            if s["kind"] == "soup":
                menuSoep += ("* {} ({})\n".format(s["name"], s["price"]))

        for m in menu["meals"]:
            if m["kind"] == "meat":
                menuHoofdgerechten += ("* Vlees: {} ({})\n".format(m["name"], m["price"]))
            elif m["kind"] == "fish":
                menuHoofdgerechten += ("* Vis: {} ({})\n".format(m["name"], m["price"]))
            elif m["kind"] == "vegetarian":
                menuHoofdgerechten += ("* Vegetarisch: {} ({})\n".format(m["name"], m["price"]))
            elif m["kind"] == "vegan":
                menuHoofdgerechten += ("* Vegan: {} ({})\n".format(m["name"], m["price"]))

        for v in menu["vegetables"]:
            menuGroenten += ("* {}\n".format(v))
    except Exception:
        menuSoep += "Restaurant gesloten"
        menuGroenten += "Restaurant gesloten"
        menuHoofdgerechten += "Restaurant gesloten"
    return menuSoep, menuHoofdgerechten, menuGroenten
