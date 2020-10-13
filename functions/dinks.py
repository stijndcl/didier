import json


def getRatios():
    return {
        ":apple:": [1, 2, 3],
        ":peach:": [2, 4, 6],
        ":banana:": [0, 20, 40],
        ":croissant:": [0, 0, 25],
        ":taco:": [0, 0, 50],
        ":burrito:": [0, 0, 0],
        ":potato:": [0, 30, 60],
        ":doughnut:": [0, 5, 10],
        ":fries:": [5, 10, 15],
        ":eggplant:": [0, 0, 10],
        ":baguette_bread:": [0, 42, 75],
        ":avocado:": [0, 50, 100],
        ":moneybag:": [0, 0, 1000]
    }


slotsHeader = ":regional_indicator_s::regional_indicator_l::regional_indicator_o::regional_indicator_t:" \
              ":regional_indicator_s:"
slotsEmptyRow = ":yellow_square::black_large_square::black_large_square::black_large_square::yellow_square:"
slotsFooter = ":yellow_square::yellow_square::yellow_square::yellow_square::yellow_square:"


def lost():
    with open("files/lost.json", "r") as fp:
        fc = json.load(fp)
    return int(fc["lost"])


def lostToday():
    with open("files/lost.json", "r") as fp:
        fc = json.load(fp)
    return int(fc["today"])
