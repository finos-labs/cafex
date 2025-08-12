"""
This module contains the DateTimeActions class that is used to perform various date and
time related actions.
"""
from datetime import datetime
from dateutil import parser
import pytz

from cafex_core.logging.logger_ import CoreLogger


class DateTimeActions:
    """
    A class used to perform various date and time related actions.

    ...

    Attributes
    ----------
    datetime_format : str
        a formatted string that defines the date and time format
    logger_class : CoreLogger
        an instance of the CoreLogger class
    logger : Logger
        a standard Python logger instance
    """

    def __init__(self, date_time_format="%Y-%m-%d %H:%M:%S"):
        """Constructs all the necessary attributes for the DateTimeActions
        object.

        Parameters
        ----------
            date_time_format : str, optional
                a formatted string that defines the date and time format
                (default is "%Y-%m-%d %H:%M:%S")
        """
        self.datetime_format = date_time_format
        self.logger_class = CoreLogger(name=__name__)
        self.logger = self.logger_class.get_logger()

    def get_current_datetime(self, to_str=False):
        """Returns the current date and time.

        If the to_str parameter is True, the date and time is returned as a string.
        Otherwise, it is returned as a datetime object.

        Examples:
            >> from cafex_core.utils.date_time_utils import DateTimeActions
            >> DateTimeActions().get_current_datetime()
            >> DateTimeActions().get_current_datetime(to_str=True)

        Args:
            to_str (bool, optional): A flag that defines the return type (default is False).

        Returns:
            datetime or str: The current date and time as a datetime object or a
            formatted string.
        """
        now = datetime.now()
        if to_str:
            return now.strftime(self.datetime_format)
        return now

    def get_current_date_time(self) -> str:
        """Returns the current date and time in ISO 8601 format with
        milliseconds.

        Examples:
            >> from cafex_core.utils.date_time_utils import DateTimeActions
            >> DateTimeActions().get_current_date_time()

        Returns:
            str: The current date and time in ISO 8601 format with milliseconds.
        """
        return (datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def get_time_by_zone(self, timezone: str) -> datetime:
        """Fetches the current time in a specified timezone.

        This method takes a timezone string and returns the current time in that timezone.

        Examples:
            >> from cafex_core.utils.date_time_utils import DateTimeActions
            >> DateTimeActions().get_time_by_zone("America/New_York")

        Args:
            timezone (str): The timezone for which the current time is to be fetched.

        Returns:
            datetime: The current time in the specified timezone.

        Raises:
            Exception: If there is an error in fetching the current time in the specified timezone.
        """
        try:
            date_utc_now = pytz.utc.localize(datetime.utcnow())
            date_now_tz = date_utc_now.astimezone(pytz.timezone(timezone))
            return date_now_tz
        except Exception as e:
            custom_exception_message = (
                "Exception in fetching today in given timezone. "
                f"Exception Details: {repr(e)}"
            )
            self.logger.exception(custom_exception_message)
            raise custom_exception_message from e

    def get_time_difference_seconds(self, end: str, start: str) -> int:
        """Returns the time difference in seconds between two times.

        Examples:
            >> from cafex_core.utils.date_time_utils import DateTimeActions
            >> DateTimeActions().get_time_difference_seconds('2025-03-04T18:29:01.295',
            '2025-03-04T18:21:01.287')

        Args:
            end (str): the end time in ISO 8601 format.
            start (str): The start time in ISO 8601 format.

        Returns:
            int: The time difference in seconds.

        Raises:
            Exception: If there is an error in calculating the time difference.
        """
        try:
            end = parser.parse(str(end))
            start = parser.parse(str(start))
            diff = end - start
            diff_in_seconds = diff.days * 24 * 60 * 60 + diff.seconds
            return diff_in_seconds
        except Exception as e:
            self.logger.error("Error in get_time_difference_seconds--> %s", str(e))
            raise e

    def seconds_to_human_readable(self, seconds: int) -> str:
        """Converts seconds to a human-readable format.

        Examples:
            >> from cafex_core.utils.date_time_utils import DateTimeActions
            >> DateTimeActions().seconds_to_human_readable(3661)

        Args:
            seconds (int): The number of seconds.

        Returns:
            str: A human-readable string representing the duration.

        Raises:
            Exception: If there is an error in converting seconds to a human-readable format.
        """
        try:
            if seconds < 60:
                return f"{seconds} second{'s' if seconds != 1 else ''}"

            minutes, seconds = divmod(seconds, 60)
            if minutes < 60:
                return (
                    f"{minutes} minute{'s' if minutes != 1 else ''}, "
                    f"{seconds} second{'s' if seconds != 1 else ''}"
                )

            hours, minutes = divmod(minutes, 60)
            if hours < 24:
                return (
                    f"{hours} hour{'s' if hours != 1 else ''}, "
                    f"{minutes} minute{'s' if minutes != 1 else ''}, "
                    f"{seconds} second{'s' if seconds != 1 else ''}"
                )

            days, hours = divmod(hours, 24)
            return (
                f"{days} day{'s' if days != 1 else ''}, "
                f"{hours} hour{'s' if hours != 1 else ''}, "
                f"{minutes} minute{'s' if minutes != 1 else ''}, "
                f"{seconds} second{'s' if seconds != 1 else ''}"
            )
        except Exception as e:
            self.logger.error("Error in seconds_to_human_readable--> %s", str(e))
            raise e
