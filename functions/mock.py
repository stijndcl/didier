import random


def mock(sentence: str):
    representations = {
        "i": "1",
        "o": "0",
        "e": "3"
    }
    switch = "[[" not in sentence
    arrRep = [letter for letter in sentence]
    retStr = ""
    for index, letter in enumerate(arrRep):
        if letter == "[":
            switch = True
        elif letter == "]":
            switch = False
        elif switch:
            if letter == "l":
                retStr += "L"
            elif letter in representations and random.randint(0, 10) > 8:
                retStr += representations[letter.lower()]
            elif letter == "i":
                retStr += "i"
            else:
                retStr += letter.upper() if index % 2 == 0 else letter.lower()
        else:
            retStr += letter
    return retStr