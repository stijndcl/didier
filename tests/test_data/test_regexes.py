from data import regexes
import re
import unittest


class TestRegexes(unittest.TestCase):
    def test_contains(self):
        pattern = {"pattern": "ABC123"}

        self.assertTrue(regexes.contains("ABC123TESTSTRING", pattern))  # Beginning
        self.assertTrue(regexes.contains("TESTABC123STRING", pattern))  # Middle
        self.assertTrue(regexes.contains("TESTSTRINGABC123", pattern))  # End
        self.assertTrue(regexes.contains("ABC123", pattern))  # Entire string

        self.assertFalse(regexes.contains("aBC123TESTSTRING", pattern))  # Wrong casing
        self.assertFalse(regexes.contains("SOMETHING ELSE", pattern))  # No match

        # Add case insensitive flag
        pattern["flags"] = re.IGNORECASE
        self.assertTrue(regexes.contains("aBC123TESTSTRING", pattern))  # Incorrect casing should now pass

    def test_steam_codes(self):
        self.assertTrue(regexes.contains("AAAAA-BBBBB-CCCCC", regexes.STEAM_CODE))  # Only letters
        self.assertTrue(regexes.contains("11111-22222-33333", regexes.STEAM_CODE))  # Only numbers
        self.assertTrue(regexes.contains("ABC12-34DEF-GHI56", regexes.STEAM_CODE))  # Both
        self.assertTrue(regexes.contains("abcde-fghij-lmnop", regexes.STEAM_CODE))  # Case insensitive flag
        self.assertTrue(regexes.contains("AAAAAA-BBBBB-CCCCC", regexes.STEAM_CODE))  # Extra characters can be in front

        self.assertFalse(regexes.contains("A-BBBBB-CCCCC", regexes.STEAM_CODE))  # First group is too small
        self.assertFalse(regexes.contains("AAAAA-BBBBBB-CCCCC", regexes.STEAM_CODE))  # Second group is too big
        self.assertFalse(regexes.contains("AA??A-#ù$B6-!ÈCMa", regexes.STEAM_CODE))  # Invalid characters
        self.assertFalse(regexes.contains("Something something communism", regexes.STEAM_CODE))  # Random string
