import random


def randomRGB():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def RGBToHEX(r, g, b):
    return "#" + str(hex(r))[2:] + str(hex(g))[2:] + str(hex(b))[2:]


def RGBToHSL(r, g, b):
    r /= 255
    g /= 255
    b /= 255
    Cmax = max(r, g, b)
    Cmin = min(r, g, b)
    delta = Cmax - Cmin

    # Hue
    h = RGBHue(r, g, b)

    # Lightness
    l = (Cmax + Cmin)/2

    # Saturation
    s = 0 if delta == 0 else delta / (1 - abs(((2 * l) - 1)))

    return round(h), round(s * 100, 2), round(l * 100, 2)


def RGBToHSV(r, g, b):
    r /= 255
    g /= 255
    b /= 255
    Cmax = max(r, g, b)
    Cmin = min(r, g, b)
    delta = Cmax - Cmin

    # Hue
    h = RGBHue(r, g, b)

    # Saturation
    s = 0 if Cmax == 0 else delta / Cmax

    # Value
    v = Cmax

    return round(h), round(s * 100, 2), round(v * 100, 2)


def RGBHue(r, g, b):
    Cmax = max(r, g, b)
    Cmin = min(r, g, b)
    delta = Cmax - Cmin

    h = -1
    if delta == 0:
        h = 0
    elif Cmax == r:
        h = 60 * (((g - b) / delta) % 6)
    elif Cmax == g:
        h = 60 * (((b - r) / delta) + 2)
    elif Cmax == b:
        h = 60 * (((r - g) / delta) + 4)

    return h
