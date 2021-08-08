from data import schedule
from datetime import datetime
from enums.platform import Platform
import pytz
from unittest import TestCase
from unittest.mock import patch


class TestSchedule(TestCase):
    def test_holiday_has_passed(self):
        tz = pytz.timezone("Europe/Brussels")
        before = datetime(2020, 8, 8, tzinfo=tz)
        during = datetime(2021, 6, 2, tzinfo=tz)
        after = datetime(2021, 8, 8, tzinfo=tz)

        holiday = schedule.Holiday([1, 6, 2021], [2, 7, 2021])

        self.assertFalse(holiday.has_passed(before))
        self.assertFalse(holiday.has_passed(during))
        self.assertTrue(holiday.has_passed(after))

    def test_timeslot_link(self):
        slot = schedule.Timeslot(schedule.Course("a"), 1234, 5678)
        self.assertEqual(None, slot.get_link_str())

        slot = schedule.Timeslot(schedule.Course("a"), 1234, 5678, online_link="link", online_platform=Platform.Zoom)
        self.assertEqual("[Zoom](link)", slot.get_link_str())

    @patch("data.schedule.Schedule.check_holidays")
    @patch("data.schedule.Schedule.load_schedule_file")
    def test_schedule_semester_over(self, mock_load, mock_check_holidays):
        mock_load.return_value = {"semester_start": [1, 2, 2020], "semester_end": [4, 5, 2021]}
        dt = datetime(2021, 8, 8, tzinfo=pytz.timezone("Europe/Brussels"))

        s = schedule.Schedule(dt, 3, 1)
        self.assertTrue(s.semester_over)

        # Check that the code stopped running in case the semester is over
        mock_check_holidays.assert_not_called()

    @patch("data.schedule.Schedule.load_schedule_file")
    def test_schedule_holidays(self, mock_load):
        mock_load.return_value = {
            "semester_start": [6, 7, 2021], "semester_end": [20, 8, 2021],
            "holidays": [
                {"start_date": [1, 8, 2021], "end_date": [10, 8, 2021]}
            ]
        }

        # During holiday
        dt = datetime(2021, 8, 8, tzinfo=pytz.timezone("Europe/Brussels"))
        s = schedule.Schedule(dt, 3, 1)
        self.assertNotEqual(None, s.current_holiday)

        # Not during holiday
        dt = datetime(2021, 8, 15, tzinfo=pytz.timezone("Europe/Brussels"))
        s = schedule.Schedule(dt, 3, 1)
        self.assertEqual(None, s.current_holiday)

    @patch("data.schedule.Schedule.load_schedule_file")
    def test_schedule_holiday_offset(self, mock_load):
        # Week 1, no holidays
        mock_load.return_value = {
            "semester_start": [2, 8, 2021], "semester_end": [20, 8, 2021]
        }

        dt = datetime(2021, 8, 6, tzinfo=pytz.timezone("Europe/Brussels"))
        s = schedule.Schedule(dt, 3, 1)
        self.assertEqual(1, s.get_week())

        # Week 1, one off-day doesn't change the week
        mock_load.return_value = {
            "semester_start": [2, 8, 2021], "semester_end": [20, 8, 2021],
            "holidays": [
                {"start_date": [5, 8, 2021], "end_date": [5, 8, 2021]}
            ]
        }

        s = schedule.Schedule(dt, 3, 1)
        self.assertEqual(1, s.get_week())

        # Week 3, with a one-week holiday in between
        mock_load.return_value = {
            "semester_start": [2, 8, 2021], "semester_end": [20, 8, 2021],
            "holidays": [
                {"start_date": [5, 8, 2021], "end_date": [5, 8, 2021]},
                {"start_date": [9, 8, 2021], "end_date": [15, 8, 2021]}
            ]
        }

        dt = datetime(2021, 8, 19, tzinfo=pytz.timezone("Europe/Brussels"))
        s = schedule.Schedule(dt, 3, 1)
        self.assertEqual(2, s.get_week())
