from data.snipe import should_snipe
import unittest
from unittest.mock import Mock


class TestSnipe(unittest.TestCase):
    def test_should_snipe(self):
        mock_message = Mock()
        mock_guild = Mock()
        mock_author = Mock()

        # Guild is None
        mock_message.guild = None
        self.assertFalse(should_snipe(mock_message))
        mock_message.guild = mock_guild

        # Author is a bot
        mock_message.author = mock_author
        mock_author.bot = True
        self.assertFalse(should_snipe(mock_message))
        mock_author.bot = False

        mock_message.content = "Some string that contains A123B-CE68S-Z6B34 a Steam code"
        self.assertFalse(should_snipe(mock_message))

        mock_message.content = "Some string that does NOT contain a Steam code"
        self.assertTrue(should_snipe(mock_message))
