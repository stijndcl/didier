from enum import Enum


class Category(Enum):
    Currency = "Currency"
    Didier = "Didier"
    Fun = "Fun"
    Gamble = "Gamble"
    Games = "Games"
    Mod = "Mod"
    Other = "Other"
    Quotes = "Quotes"
    Random = "Random"
    School = "School"
    Sports = "Sports"
    Words = "Words"


# Returns a list of all categories (names)
def categories(is_mod=False):
    cat = [e.value for e in Category]
    # Don't show mod commands to random people
    if is_mod:
        return cat
    cat.remove(Category.Mod.value)
    return cat


# Gets the Enum associated with a term
def getCategory(term, is_mod=False):
    for category in Category:
        if category.value.lower() == term.lower():
            # Check if user is trying to access mod commands
            if category != Category.Mod or (category == Category.Mod and is_mod):
                return category
    return None
