def title_case(string):
    return " ".join(capitalize(word) for word in string.split(" "))


def capitalize(string):
    if len(string) > 1:
        return string[0].upper() + string[1:].lower()
    return string[0].upper()


def leading_zero(string, size=2):
    string = str(string)
    while len(string) < size:
        string = "0" + string
    return string
