from datetime import datetime
from functions import timeFormatters
import unittest


class TestTimeFormatters(unittest.TestCase):
    def test_leadingZero(self):
        self.assertEqual("0123", timeFormatters.leadingZero("123"))
        self.assertEqual("0123", timeFormatters.leadingZero("0123"))

    def test_delimiter(self):
        self.assertEqual("01:23", timeFormatters.delimiter("0123"))
        self.assertEqual("01.23", timeFormatters.delimiter("0123", delim="."))

    def test_timeFromInt(self):
        self.assertEqual("01:23", timeFormatters.timeFromInt(123))
        self.assertEqual("12:34", timeFormatters.timeFromInt(1234))

    def test_fromArray(self):
        # Only day/month/year
        d, m, y = 1, 2, 2021
        inp = [d, m, y]

        dt = timeFormatters.fromArray(inp)
        self.assertEqual(d, dt.day)
        self.assertEqual(m, dt.month)
        self.assertEqual(y, dt.year)

        # Also hours/minutes/seconds
        d, m, y, hh, mm, ss = 1, 2, 2021, 1, 2, 3
        inp = [d, m, y, hh, mm, ss]

        dt = timeFormatters.fromArray(inp)
        self.assertEqual(d, dt.day)
        self.assertEqual(m, dt.month)
        self.assertEqual(y, dt.year)
        self.assertEqual(hh, dt.hour)
        self.assertEqual(mm, dt.minute)
        self.assertEqual(ss, dt.second)

    def test_skipWeekends(self):
        # Already a weekday
        weekday = datetime(2021, 8, 11)
        skipped = timeFormatters.skip_weekends(weekday)
        self.assertEqual(weekday, skipped)

        # Weekend
        weekend = datetime(2021, 8, 7)
        skipped = timeFormatters.skip_weekends(weekend)
        self.assertEqual(0, skipped.weekday())

    def test_forwardToWeekday(self):
        mo = datetime(2021, 8, 10)
        # Before
        forwarded = timeFormatters.forward_to_weekday(mo, 2)
        self.assertEqual(1, (forwarded - mo).days)

        # Same day
        forwarded = timeFormatters.forward_to_weekday(mo, 1)
        self.assertEqual(7, (forwarded - mo).days)

        # After
        forwarded = timeFormatters.forward_to_weekday(mo, 0)
        self.assertEqual(6, (forwarded - mo).days)
