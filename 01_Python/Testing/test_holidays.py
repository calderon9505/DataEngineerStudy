import unittest
from unittest.mock import patch

from holidays import get_holidays
import requests


class TestHolidays(unittest.TestCase):
    @patch.object(requests, "get", side_effect=requests.exceptions.Timeout)
    def test_get_holidays_timeout(self, mock_requests):
        with self.assertRaises(requests.exceptions.Timeout):
            get_holidays()


if __name__ == "__main__":
    unittest.main()
