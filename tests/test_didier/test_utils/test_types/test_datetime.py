import datetime

import pytest

from didier.utils.types.datetime import str_to_date


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
