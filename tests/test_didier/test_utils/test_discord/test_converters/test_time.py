from datetime import date

from freezegun import freeze_time

from didier.utils.discord.converters.time import date_converter


@freeze_time("2022-08-20")
def test_date_converter_empty_returns_today():
    """Test that the date converter returns today by default"""
    result = date_converter(None)
    assert result == date.today()

    result = date_converter("")
    assert result == date.today()


@freeze_time("2022-08-20")
def test_date_converter_keywords_tomorrow():
    """Test that the date converter works correctly for +1-offset keywords"""
    result = date_converter("tomorrow")
    assert (result.day, result.month, result.year) == (21, 8, 2022)

    result = date_converter("tmrw")
    assert (result.day, result.month, result.year) == (21, 8, 2022)

    result = date_converter("morgen")
    assert (result.day, result.month, result.year) == (21, 8, 2022)


@freeze_time("2022-08-20")
def test_date_converter_keywords_two_days():
    """Test that the date converter works correctly for +2-offset keywords"""
    result = date_converter("overmorgen")
    assert (result.day, result.month, result.year) == (22, 8, 2022)


@freeze_time("2022-08-20")  # This is a Saturday
def test_date_converter_weekdays_english():
    """Test that the date converter works correctly for weekdays (English version)"""
    # Full
    result = date_converter("monday")
    assert (result.day, result.month, result.year) == (22, 8, 2022)

    result = date_converter("tuesday")
    assert (result.day, result.month, result.year) == (23, 8, 2022)

    result = date_converter("wednesday")
    assert (result.day, result.month, result.year) == (24, 8, 2022)

    result = date_converter("thursday")
    assert (result.day, result.month, result.year) == (25, 8, 2022)

    result = date_converter("friday")
    assert (result.day, result.month, result.year) == (26, 8, 2022)

    result = date_converter("saturday")
    assert (result.day, result.month, result.year) == (27, 8, 2022)

    result = date_converter("sunday")
    assert (result.day, result.month, result.year) == (21, 8, 2022)

    # Abbreviated
    result = date_converter("mon")
    assert (result.day, result.month, result.year) == (22, 8, 2022)

    result = date_converter("tue")
    assert (result.day, result.month, result.year) == (23, 8, 2022)

    result = date_converter("wed")
    assert (result.day, result.month, result.year) == (24, 8, 2022)

    result = date_converter("thu")
    assert (result.day, result.month, result.year) == (25, 8, 2022)

    result = date_converter("fri")
    assert (result.day, result.month, result.year) == (26, 8, 2022)

    result = date_converter("sat")
    assert (result.day, result.month, result.year) == (27, 8, 2022)

    result = date_converter("sun")
    assert (result.day, result.month, result.year) == (21, 8, 2022)


@freeze_time("2022-08-20")  # This is a Saturday
def test_date_converter_weekdays_dutch():
    """Test that the date converter works correctly for weekdays (Dutch version)"""
    # Full
    result = date_converter("maandag")
    assert (result.day, result.month, result.year) == (22, 8, 2022)

    result = date_converter("dinsdag")
    assert (result.day, result.month, result.year) == (23, 8, 2022)

    result = date_converter("woensdag")
    assert (result.day, result.month, result.year) == (24, 8, 2022)

    result = date_converter("donderdag")
    assert (result.day, result.month, result.year) == (25, 8, 2022)

    result = date_converter("vrijdag")
    assert (result.day, result.month, result.year) == (26, 8, 2022)

    result = date_converter("zaterdag")
    assert (result.day, result.month, result.year) == (27, 8, 2022)

    result = date_converter("zondag")
    assert (result.day, result.month, result.year) == (21, 8, 2022)

    # Abbreviated
    result = date_converter("ma")
    assert (result.day, result.month, result.year) == (22, 8, 2022)

    result = date_converter("di")
    assert (result.day, result.month, result.year) == (23, 8, 2022)

    result = date_converter("woe")
    assert (result.day, result.month, result.year) == (24, 8, 2022)

    result = date_converter("do")
    assert (result.day, result.month, result.year) == (25, 8, 2022)

    result = date_converter("vrij")
    assert (result.day, result.month, result.year) == (26, 8, 2022)

    result = date_converter("za")
    assert (result.day, result.month, result.year) == (27, 8, 2022)

    result = date_converter("zo")
    assert (result.day, result.month, result.year) == (21, 8, 2022)
