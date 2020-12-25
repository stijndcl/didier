def check(content, earlier=[]):
    # No arguments passed
    if len(content) < 1:
        return False, ["Controleer je argumenten."]

    # This command should work case insensitive
    for i, word in enumerate(content):
        content[i] = word.lower()

    invalid_characters = []

    # Check valid characters
    for word in content:
        for letter in word:
            if letter not in allowedCharacters():
                invalid_characters.append(letter)

    # Get uniques
    invalid_characters = list(set(invalid_characters))

    # Invalid char was passed
    if len(invalid_characters) == 1:
        return False, ["**{}** is geen geldige letter.".format(invalid_characters[0])]

    # Multiple invalid chars were passed
    if len(invalid_characters) > 1:
        return False, ["**{}** en **{}** zijn geen geldige letters.".format(
            ", ".join(invalid_characters[:-1]), invalid_characters[-1]
        )]

    # Check if ID was passed or not, remove from list of words if so
    # Also join everything into one word
    if content[-1].isdigit() and len(content[-1]) > 10:
        content[0] = "".join(content[:-1])
    else:
        content[0] = "".join(content)

    # In case a space was passed using "a b", strip it out as well
    content[0] = content[0].replace(" ", "")

    doubles = getDoubles()

    nums = getNumbers()

    specials = getSpecialCharacters()

    unidic = getUnicodeDict()

    # Check for reactions that were already added earlier
    for x in earlier:
        # Check if reaction is a random reaction or a letter/number
        if x in unidic.values():
            word = ""
            # Find the key used, remove it from the list of remaining available letters
            for key in unidic:
                if unidic[key] == x:
                    word = key
                    break

            del unidic[word]

            # Same thing for doubles
            for k in list(doubles.keys()):
                if word in doubles[k]:
                    doubles[k].remove(word)
                    if len(doubles[k]) == 0:
                        del doubles[k]
                    break

            # Same thing for numbers
            for k in list(nums.keys()):
                if nums[k] == word:
                    del nums[k]

            # Same thing for special characters
            for k in list(specials.keys()):
                if word in specials[k]:
                    specials[k].remove(word)
                    if len(specials[k]) == 0:
                        del specials[k]

    # Check if earlier letters made this reaction impossible
    for letter in content[0]:
        c = content[0].count(letter)

        # If a letter was added three times, but there is only two, that's an issue
        if c > 2 and letter not in doubles:
            return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]
        elif c > 2 and letter in doubles and len(doubles[letter]) < c:
            return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]

    # Array of emoji's
    arr = []

    # Start checking every character
    for letter in content[0]:
        # Letters
        if letter.isalpha():
            reg_ind = "regional_indicator_{}".format(letter)
            zb = "zb_{}".format(letter.upper())

            # Check if this letter has not been added yet
            if reg_ind in unidic and unidic[reg_ind] not in arr:
                arr.append(unidic[reg_ind])

                # Remove this letter as an option from the list of doubles
                if letter in doubles:
                    doubles[letter] = doubles[letter][1:]

            # Check for Zandbak copies
            elif zb in unidic and unidic[zb] not in arr:
                arr.append(unidic[zb])

                # Remove this letter as an option from the list of doubles
                if letter in doubles:
                    doubles[letter] = doubles[letter][1:]
            # Letter has been added before, but there's a double for it
            elif letter in doubles:
                if len(doubles[letter]) == 0:
                    return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]

                # Remove the number-equivalent from nums if it is used as a substitute here
                arr.append(unidic[doubles[letter][0]])
                if doubles[letter][0] in nums.values():
                    for k in nums:
                        if nums[k] == doubles[letter][0]:
                            del nums[k]
                            break

                # Remove this character from the list of available doubles
                doubles[letter] = doubles[letter][1:]

                # Remove from the dictionary of doubles if the last double was used
                if len(doubles[letter]) == 0:
                    del doubles[letter]
            else:
                return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]
        # Special characteres
        elif letter in specials:
            # No more options
            if len(specials[letter]) == 0:
                return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]

            # Add it to the array & remove from the list of options
            arr.append(unidic[specials[letter][0]])
            specials[letter].pop(0)

            if len(specials[letter]) == 0:
                del specials[letter]
        # Number
        else:
            # Number was used before as a double for a letter
            if letter not in nums:
                return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]

            arr.append(unidic[nums[letter]])

            # Add this emoji to the array, remove it as a double everywhere
            for x in doubles:
                # Remove this number as a substitute if it is used anywhere
                if nums[letter] == doubles[x][-1]:
                    doubles[x] = doubles[x][:-1]
                    if len(doubles[x]) == 0:
                        del doubles[x]
                    break
    return True, arr


def allowedCharacters():
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', "!", "?", "#", "*", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def getDoubles():
    doubles = {
        "a": ["regional_indicator_a", "zb_A", "a", "four"],
        "b": ["regional_indicator_b", "zb_B", "b"],
        "o": ["regional_indicator_o", "zb_O", "o2", "zero"],
        "i": ["regional_indicator_i", "zb_I", "information_source", "one"],
        "p": ["regional_indicator_p", "zb_P", "parking"],
        "m": ["regional_indicator_m", "zb_M", "m"],
        "s": ["regional_indicator_s", "zb_S", "five"],
        "g": ["regional_indicator_g", "zb_G", "six"],
        "e": ["regional_indicator_e", "zb_E", "three"],
        "!": ["exclamation", "grey_exclamation"],
        "?": ["question", "grey_question"]
    }

    return doubles


def getNumbers():
    nums = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine"
    }

    return nums


def getSpecialCharacters():
    specials = {
        "?": ["question", "grey_question"],
        "!": ["exclamation", "grey_exclamation"],
        "*": ["asterisk"],
        "#": ["hash"]
    }

    return specials


def getUnicodeDict():
    unidic = {
        "regional_indicator_a": "🇦",
        "regional_indicator_b": "🇧",
        "regional_indicator_c": "🇨",
        "regional_indicator_d": "🇩",
        "regional_indicator_e": "🇪",
        "regional_indicator_f": "🇫",
        "regional_indicator_g": "🇬",
        "regional_indicator_h": "🇭",
        "regional_indicator_i": "🇮",
        "regional_indicator_j": "🇯",
        "regional_indicator_k": "🇰",
        "regional_indicator_l": "🇱",
        "regional_indicator_m": "🇲",
        "regional_indicator_n": "🇳",
        "regional_indicator_o": "🇴",
        "regional_indicator_p": "🇵",
        "regional_indicator_q": "🇶",
        "regional_indicator_r": "🇷",
        "regional_indicator_s": "🇸",
        "regional_indicator_t": "🇹",
        "regional_indicator_u": "🇺",
        "regional_indicator_v": "🇻",
        "regional_indicator_w": "🇼",
        "regional_indicator_x": "🇽",
        "regional_indicator_y": "🇾",
        "regional_indicator_z": "🇿",
        "zb_A": "<:zb_A:792094798516453387>",
        "zb_B": "<:zb_B:792094798986346507>",
        "zb_C": "<:zb_C:792094799724412958>",
        "zb_D": "<:zb_D:792094799984984124>",
        "zb_E": "<:zb_E:792094800093380649>",
        "zb_F": "<:zb_F:792094799657566278>",
        "zb_G": "<:zb_G:792094800014606336>",
        "zb_H": "<:zb_H:792094799745908736>",
        "zb_I": "<:zb_I:792094799620079626>",
        "zb_J": "<:zb_J:792094799800958976>",
        "zb_K": "<:zb_K:792094800069263420>",
        "zb_L": "<:zb_L:792094754036383755>",
        "zb_M": "<:zb_M:792094704674013234>",
        "zb_N": "<:zb_N:792094660281630751>",
        "zb_O": "<:zb_O:792094628848467998>",
        "zb_P": "<:zb_P:792094590793940992>",
        "zb_Q": "<:zb_Q:792094558417584138>",
        "zb_R": "<:zb_R:792094529951498260>",
        "zb_S": "<:zb_S:792094506526572564>",
        "zb_T": "<:zb_T:792094451530334228>",
        "zb_U": "<:zb_U:792094420195082240>",
        "zb_V": "<:zb_V:792094388716437544>",
        "zb_W": "<:zb_W:792094342285754378>",
        "zb_X": "<:zb_X:792094308412293190>",
        "zb_Y": "<:zb_Y:792094270445322270>",
        "zb_Z": "<:zb_Z:792094240212779028>",
        "a": "🅰️",
        "b": "🅱️",
        "o2": "🅾️",
        "information_source": "ℹ️",
        "parking": "🅿️",
        "m": "Ⓜ️",
        "zero": "0⃣",
        "one": "1️⃣",
        "two": "2️⃣",
        "three": "3️⃣",
        "four": "4️⃣",
        "five": "5️⃣",
        "six": "6️⃣",
        "seven": "7️⃣",
        "eight": "8️⃣",
        "nine": "9️⃣",
        "exclamation": "❗",
        "grey_exclamation": "❕",
        "question": "❓",
        "grey_question": "❔",
        "hash": "#️⃣",
        "asterisk": "*️⃣"
    }

    return unidic


# Returns a list of all emoji's that exist for a char
def getAllVariants(char: str):
    variants = []

    # Letter
    reg_ind = "regional_indicator_{}".format(char)
    if reg_ind in getUnicodeDict():
        variants.append(reg_ind)
        variants.append("zb_{}".format(char.upper()))

    # Number
    elif char in getNumbers():
        variants.append(getNumbers()[char])

    # Special Character
    elif char in getSpecialCharacters():
        for letter in getSpecialCharacters()[char]:
            variants.append(letter)

    # Get all doubles
    if char in getDoubles():
        for letter in getDoubles()[char]:
            variants.append(letter)

    # Remove doubles that might have slipped in
    # Use a list here to keep the order!
    uniques = []

    print(variants)
    for var in variants:
        rep = ":" + var + ":"

        # Zandbak copies are formatted differently
        if var.startswith("zb_"):
            rep = getUnicodeDict()[var]

        if rep not in uniques:
            uniques.append(rep)

    return uniques
