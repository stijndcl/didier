from enum import Enum


class Numbers(Enum):
    K = 1000
    M = 1000000
    B = 1000000000
    t = 1000000000000
    q = 1000000000000000
    Q = 1000000000000000000
    s = 1000000000000000000000
    S = 1000000000000000000000000


def getRep(number):
    number = int(number)
    best = None
    for entry in Numbers:
        if entry.value <= number:
            best = entry
        else:
            return str(round(number//best.value)) + best.name

    return number
