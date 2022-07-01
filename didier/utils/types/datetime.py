def int_to_weekday(number: int) -> str:  # pragma: no cover # it's useless to write a test for this
    """Get the Dutch name of a weekday from the number"""
    return ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"][number]
