import pytest

from didier.exceptions import NoMatch, expect


def test_expect_none_raises():
    """Test that expect() raises an error if the input entity is None"""
    with pytest.raises(NoMatch):
        expect(None, entity_type="", argument="")


def test_expect_not_none_returns():
    """Test that expect() returns the argument if it isn't None"""
    arg = "Some input string"
    assert expect(arg, entity_type="", argument="") == arg
