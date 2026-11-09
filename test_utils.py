# test_utils.py
import unittest
from datetime import date

from utils import format_duration, get_date_range

TODAY = date(2026, 10, 31)   # thứ Bảy


class FormatDurationTests(unittest.TestCase):

    def test_seconds_only(self):
        self.assertEqual(format_duration(45), "45 giây")

    def test_minutes_and_seconds(self):
        self.assertEqual(format_duration(125), "2 phút 5 giây")

    def test_hours_and_minutes(self):
        self.assertEqual(format_duration(3700), "1 giờ 1 phút")


class DateRangeTests(unittest.TestCase):

    def test_today(self):
        self.assertEqual(
            get_date_range("Hôm nay", TODAY),
            ("2026-10-31", "2026-10-31")
        )

    def test_week_starts_on_monday(self):
        self.assertEqual(
            get_date_range("Tuần này", TODAY),
            ("2026-10-26", "2026-10-31")
        )

    def test_month_starts_on_first_day(self):
        self.assertEqual(
            get_date_range("Tháng này", TODAY),
            ("2026-10-01", "2026-10-31")
        )

    def test_all_starts_at_year_one(self):
        self.assertEqual(
            get_date_range("Tất cả", TODAY),
            ("0001-01-01", "2026-10-31")
        )


if __name__ == "__main__":
    unittest.main()