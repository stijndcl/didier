def clap(content: str):
    if content == "":
        return "Dit is geen geldig bericht"
    text = "".join([str(s).lower() if s.isdigit() or s.isalpha() else "" for s in content])
    newStr = ":clap: " + " :clap: ".join(fetch("regional_indicator_{}".format(char) if char.isalpha() else char) for char in text) + " :clap:"
    return newStr if 0 < len(newStr) <= 1100 else "Dit is geen geldig bericht."


def fetch(char):
    dic = {
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
        "zero": "0⃣",
        "one": "1️⃣",
        "two": "2️⃣",
        "three": "3️⃣",
        "four": "4️⃣",
        "five": "5️⃣",
        "six": "6️⃣",
        "seven": "7️⃣",
        "eight": "8️⃣",
        "nine": "9️⃣"
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

    return dic[str(char)] if char[-1].isalpha() else dic[nums[str(char)]]