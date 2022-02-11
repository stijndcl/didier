from functions.scrapers import sporza
import unittest


class TestSporzaScraper(unittest.TestCase):
    def test_find_matchweek(self):
        """
        This tests if the structure of the HTML is still what we expect it to be,
        as Sporza changes it from time to time.
        """
        # This will throw an error if the argument was not a proper integer
        week = int(sporza.getMatchweek())
        self.assertGreater(week, 0)
