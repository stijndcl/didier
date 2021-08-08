from data import schedule
from datetime import datetime
import pytz
import unittest


class TestSchedule(unittest.TestCase):
    def test_holiday_has_passed(self):
        tz = pytz.timezone("Europe/Brussels")
        before = datetime(2020, 8, 8, tzinfo=tz)
        during = datetime(2021, 6, 2, tzinfo=tz)
        after = datetime(2021, 8, 8, tzinfo=tz)

        holiday = schedule.Holiday([1, 6, 2021], [2, 7, 2021])

        self.assertFalse(holiday.has_passed(before))
        self.assertFalse(holiday.has_passed(during))
        self.assertTrue(holiday.has_passed(after))
