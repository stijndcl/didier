import pytest

from didier.utils.discord.converters import numbers


def test_abbreviated_int():
    """Test abbreviated_number for a regular int"""
    assert numbers.abbreviated_number("500") == 500


def test_abbreviated_float_errors():
    """Test abbreviated_number for a float"""
    with pytest.raises(ValueError):
        numbers.abbreviated_number("5.4")


def test_abbreviated_int_unit():
    """Test abbreviated_number for an int combined with a unit"""
    assert numbers.abbreviated_number("20k") == 20000


def test_abbreviated_int_unknown_unit():
    """Test abbreviated_number for an int combined with an unknown unit"""
    with pytest.raises(ValueError):
        numbers.abbreviated_number("20p")


def test_abbreviated_float_unit():
    """Test abbreviated_number for a float combined with a unit"""
    assert numbers.abbreviated_number("20.5k") == 20500


def test_abbreviated_float_unknown_unit():
    """Test abbreviated_number for a float combined with an unknown unit"""
    with pytest.raises(ValueError):
        numbers.abbreviated_number("20.5p")


def test_abbreviated_no_number():
    """Test abbreviated_number for unparseable content"""
    with pytest.raises(ValueError):
        numbers.abbreviated_number("didier")


def test_abbreviated_float_floors():
    """Test abbreviated_number for a float that is longer than the unit
    Example:
        5.3k is 5300, but 5.3001k is 5300.1
    """
    assert numbers.abbreviated_number("5.3001k") == 5300
