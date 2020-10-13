def check(content, earlier=[]):
    if len(content) < 1:
        return False, ["Controleer je argumenten."]
    if any(not (x.isalpha() or x.isdigit() or x in ["#", "*", "!", "?"]) for x in content):
        return False, ["Dit is geen geldig woord."]
    if content[-1].isdigit() and len(content[-1]) > 10:
        content[0] = "".join(x for x in content[:-1])
    else:
        content[0] = "".join(x for x in content)

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

    specials = {
        "?": ["question", "grey_question"],
        "!": ["exclamation", "grey_exclamation"],
        "*": ["asterisk"],
        "#": ["hash"]
    }

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

    for x in earlier:
        if x in unidic.values():
            word = ""
            for key in unidic:
                if unidic[key] == x:
                    word = key
                    break
            del unidic[word]
            for k in list(doubles.keys()):
                if word in doubles[k]:
                    doubles[k].remove(word)
                    if len(doubles[k]) == 0:
                        del doubles[k]
                    break
            for k in list(nums.keys()):
                if nums[k] == word:
                    del nums[k]
            for k in list(specials.keys()):
                if word in specials[k]:
                    specials[k].remove(word)
                    if len(specials[k]) == 0:
                        del specials[k]

    for letter in content[0]:
        c = content[0].count(letter)
        if c != 1 and letter not in doubles:
            return False, ["Dit is geen geldig woord."]
        elif c > 1 and letter in doubles and len(doubles[letter]) < c:
            return False, ["Dit is geen geldig woord."]

    arr = []
    for letter in content[0]:
        if letter.isalpha():
            if "regional_indicator_{}".format(letter) in unidic and unidic["regional_indicator_{}".format(letter)] not in arr:
                arr.append(unidic["regional_indicator_{}".format(letter)])
                if letter in doubles:
                    doubles[letter] = doubles[letter][1:]
            elif letter in doubles:
                if len(doubles[letter]) == 0:
                    return False, ["Dit is geen geldig woord."]
                # Remove the number-equivalent from nums if it is used as a substitute here
                arr.append(unidic[doubles[letter][0]])
                if doubles[letter][0] in nums.values():
                    for k in nums:
                        if nums[k] == doubles[letter][0]:
                            del nums[k]
                            break
                doubles[letter] = doubles[letter][1:]
                if len(doubles[letter]) == 0:
                    del doubles[letter]
            else:
                return False, ["Dit is geen geldig woord."]
        elif letter in specials:
            if len(specials[letter]) == 0:
                return False, ["Dit is geen geldig woord."]
            arr.append(unidic[specials[letter][0]])
            specials[letter].pop(0)
            if len(specials[letter]) == 0:
                del specials[letter]
        else:
            if letter not in nums:
                return False, ["Dit is geen geldig woord."]
            arr.append(unidic[nums[letter]])
            for x in doubles:
                # Remove this number as a substitute if it is used anywhere
                if nums[letter] == doubles[x][-1]:
                    doubles[x] = doubles[x][:-1]
                    if len(doubles[x]) == 0:
                        del doubles[x]
                    break
    return True, arr
