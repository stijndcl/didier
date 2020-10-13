import math


def calculate_level(xp):
    xp = int(xp)
    level = 1

    while level_to_xp(level + 1) < xp:
        level += 1

    return level


def level_to_xp(level):
    return math.floor(sum((equate(lvl) for lvl in range(1, level))) / 4)


def equate(xp):
    return math.floor(xp + 300 * (2 ** (xp / 7.0)))
