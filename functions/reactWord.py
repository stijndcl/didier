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

        # If a letter was added twice, but there is only one, that's an issue
        if c != 1 and letter not in doubles:
            return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]
        elif c > 1 and letter in doubles and len(doubles[letter]) < c:
            return False, ["Er zijn niet genoeg **{}**'s om dit woord te reacten.".format(letter)]

    # Array of emoji's
    arr = []

    # Start checking every character
    for letter in content[0]:
        # Letters
        if letter.isalpha():
            # Check if this letter has not been added yet
            if "regional_indicator_{}".format(letter) in unidic and unidic["regional_indicator_{}".format(letter)] not in arr:
                arr.append(unidic["regional_indicator_{}".format(letter)])

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
        "a": ["regional_indicator_a", "a", "four"],
        "b": ["regional_indicator_b", "b"],
        "o": ["regional_indicator_o", "o2", "zero"],
        "i": ["regional_indicator_i", "information_source", "one"],
        "p": ["regional_indicator_p", "parking"],
        "m": ["regional_indicator_m", "m"],
        "s": ["regional_indicator_s", "five"],
        "g": ["regional_indicator_g", "six"],
        "e": ["regional_indicator_e", "three"],
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

    # Number
    elif char in getNumbers():
        variants.append(getNumbers()[char])

    # Special Character
    elif char in getSpecialCharacters():
        variants.append(getSpecialCharacters()[char])

    # Get all doubles
    if char in getDoubles():
        for letter in getDoubles()[char]:
            variants.append(letter)

    # Remove doubles that might have slipped in
    # Use a list here to keep the order!
    uniques = []

    for var in variants:
        rep = ":" + var + ":"
        if rep not in uniques:
            uniques.append(rep)

    return uniques
