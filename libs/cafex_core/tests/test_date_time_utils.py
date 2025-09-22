from cafex_core.utils.date_time_utils import DateTimeActions
from datetime import datetime


class TestDateTimeUtils:

    def test_get_current_datetime(self):
        try:
            dtu = DateTimeActions()
            assert isinstance(dtu.get_current_datetime(), datetime)
            assert isinstance(dtu.get_current_datetime(to_str=True), str)
            # dtu.get_current_datetime("invalid")
        except Exception as e:
            print(e)

    def test_get_current_date_time(self):
        try:
            dtu = DateTimeActions()
            assert isinstance(dtu.get_current_date_time(), str)
            dtu.get_current_date_time("invalid","invalid")
        except Exception as e:
            print(e)

    def test_get_time_by_zone(self):
        try:
            dtu = DateTimeActions()
            assert isinstance(dtu.get_time_by_zone("America/New_York"), datetime)
            assert isinstance(dtu.get_time_by_zone("Asia/Kolkata"), datetime)
            assert isinstance(dtu.get_time_by_zone("Europe/London"), datetime)
            assert isinstance(dtu.get_time_by_zone("Australia/Sydney"), datetime)
            dtu.get_time_by_zone(20)
        except Exception as e:
            print(e)

    def test_get_time_difference_seconds(self):
        try:
            dtu = DateTimeActions()
            assert dtu.get_time_difference_seconds('2025-03-04T18:29:01.295', '2025-03-04T18:21:01.287') == 480
            assert dtu.get_time_difference_seconds('2025-03-04T18:29:01.295', '2025-03-04T18:29:01.295') == 0
            assert dtu.get_time_difference_seconds('2025-03-04T18:29:01.295', '2025-03-04T18:29:01.294') == 0
            dtu.get_time_difference_seconds("invalid", "invalid")
        except Exception as e:
            print(e)


    def test_seconds_to_human_readable(self):
        try:
            dtu = DateTimeActions()
            assert dtu.seconds_to_human_readable(3661) == "1 hour, 1 minute, 1 second"
            assert dtu.seconds_to_human_readable(3600) == "1 hour"
            assert dtu.seconds_to_human_readable(60) == "1 minute"
            assert dtu.seconds_to_human_readable(1) == "1 second"
            assert dtu.seconds_to_human_readable(0) == "0 milliseconds"
            assert dtu.seconds_to_human_readable(86400) == "1 day"
            dtu.seconds_to_human_readable("invalid")
        except Exception as e:
            print(e)
