from enums.numbers import getRep as rep


def clamp(value, bottom, top):
    if value < bottom:
        return bottom

    if value > top:
        return top

    return value


def getRep(number, top):
    number = int(number)
    if number < top:
        return "{:,}".format(number)
    return rep(number)
