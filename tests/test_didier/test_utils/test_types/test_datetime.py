import datetime

import pytest
from freezegun import freeze_time

from didier.utils.types.datetime import parse_dm_string, str_to_date


@freeze_time("2022-08-20")
def test_parse_dm_string_ddmm():
    """Test parsing DD/MM"""
    result = parse_dm_string("23/08")
    assert (result.day, result.month, result.year) == (23, 8, 2022)

    result = parse_dm_string("8/9")
    assert (result.day, result.month, result.year) == (8, 9, 2022)


def test_parse_dm_string_dm_too_long_raises():
    """Test parsing DD/MM format when something longer is passed in"""
    with pytest.raises(ValueError):
        parse_dm_string("23/08/2022")


def test_parse_dm_string_dm_garbage():
    """Test parsing DD/MM format when something invalid is passed in"""
    with pytest.raises(ValueError):
        parse_dm_string("AC/DC")


def test_parse_dm_string_semantic():
    """Test parsing date strings in the [DAY] [MONTH] and [MONTH] [DAY] formats"""
    result = parse_dm_string("23rd november")
    assert (result.day, result.month, result.year) == (23, 11, 2022)

    result = parse_dm_string("23 nov")
    assert (result.day, result.month, result.year) == (23, 11, 2022)

    result = parse_dm_string("23ste november")
    assert (result.day, result.month, result.year) == (23, 11, 2022)

    result = parse_dm_string("november 23rd")
    assert (result.day, result.month, result.year) == (23, 11, 2022)

    result = parse_dm_string("nov 23")
    assert (result.day, result.month, result.year) == (23, 11, 2022)


def test_parse_dm_string_unparseable_raises():
    """Test that any other input raises an error"""
    with pytest.raises(ValueError):
        parse_dm_string("WhateverThisMayBe")


def test_str_to_date_single_valid():
    """Test parsing a string for a single possibility (default)"""
    result = str_to_date("23/11/2001")
    assert result == datetime.date(year=2001, month=11, day=23)


def test_str_to_date_single_invalid():
    """Test parsing a string for an invalid string"""
    # Invalid format
    with pytest.raises(ValueError):
        str_to_date("23/11/01")

    # Invalid date
    with pytest.raises(ValueError):
        str_to_date("69/42/0")


def test_str_to_date_multiple_valid():
    """Test parsing a string for multiple possibilities"""
    result = str_to_date("23/11/01", formats=["%d/%m/%Y", "%d/%m/%y"])
    assert result == datetime.date(year=2001, month=11, day=23)


def test_str_to_date_multiple_invalid():
    """Test parsing a string for multiple possibilities when none are valid"""
    with pytest.raises(ValueError):
        str_to_date("2001/01/02", formats=["%d/%m/%Y", "%d/%m/%y"])
