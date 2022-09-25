from unittest.mock import MagicMock

from didier import Didier
from didier.utils.discord.prefix import get_prefix


def test_get_prefix_didier(mock_client: Didier):
    """Test the "didier" prefix"""
    mock_message = MagicMock()
    mock_message.content = "didier test"
    assert get_prefix(mock_client, mock_message) == "didier "


def test_get_prefix_didier_cased(mock_client: Didier):
    """Test the "didier" prefix with random casing"""
    mock_message = MagicMock()
    mock_message.content = "Didier test"
    assert get_prefix(mock_client, mock_message) == "Didier "

    mock_message = MagicMock()
    mock_message.content = "DIDIER test"
    assert get_prefix(mock_client, mock_message) == "DIDIER "

    mock_message = MagicMock()
    mock_message.content = "DiDiEr test"
    assert get_prefix(mock_client, mock_message) == "DiDiEr "


def test_get_prefix_default(mock_client: Didier):
    """Test the fallback prefix (used when nothing matched)"""
    mock_message = MagicMock()
    mock_message.content = "random message"
    assert get_prefix(mock_client, mock_message) == "didier"


def test_get_prefix_big_d(mock_client: Didier):
    """Test the "big d" prefix"""
    mock_message = MagicMock()
    mock_message.content = "big d test"
    assert get_prefix(mock_client, mock_message) == "big d "


def test_get_prefix_big_d_cased(mock_client: Didier):
    """Test the "big d" prefix with random casing"""
    mock_message = MagicMock()
    mock_message.content = "Big d test"
    assert get_prefix(mock_client, mock_message) == "Big d "

    mock_message = MagicMock()
    mock_message.content = "Big D test"
    assert get_prefix(mock_client, mock_message) == "Big D "

    mock_message = MagicMock()
    mock_message.content = "BIG D test"
    assert get_prefix(mock_client, mock_message) == "BIG D "


def test_get_prefix_mention_username(mock_client: Didier):
    """Test the @mention prefix when mentioned by username"""
    mock_message = MagicMock()
    prefix = f"<@{mock_client.user.id}> "
    mock_message.content = f"{prefix}test"

    assert get_prefix(mock_client, mock_message) == prefix


def test_get_prefix_mention_nickname(mock_client: Didier):
    """Test the @mention prefix when mentioned by server nickname"""
    mock_message = MagicMock()
    prefix = f"<@!{mock_client.user.id}> "
    mock_message.content = f"{prefix}test"

    assert get_prefix(mock_client, mock_message) == prefix


def test_get_prefix_whitespace(mock_client: Didier):
    """Test that variable whitespace doesn't matter"""
    mock_message = MagicMock()
    mock_message.content = "didiertest"
    assert get_prefix(mock_client, mock_message) == "didier"

    mock_message = MagicMock()
    mock_message.content = "didier  test"
    assert get_prefix(mock_client, mock_message) == "didier  "
