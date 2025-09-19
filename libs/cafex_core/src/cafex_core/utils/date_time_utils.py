"""This module contains the DateTimeActions class that is used to perform various date and time
related actions.
"""

from datetime import datetime, timezone

import pytz
from dateutil import parser

from ..logging.logger_ import CoreLogger


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
        """
        Constructs all the necessary attributes for the DateTimeActions object.

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
        """
        Returns the current date and time.

        If the to_str parameter is True, the date and time is returned as a string.
        Otherwise, it is returned as a datetime object.

        Examples:
            >>> from cafex_core.utils.date_time_utils import DateTimeActions
            >>> DateTimeActions().get_current_datetime()
            >>> DateTimeActions().get_current_datetime(to_str=True)

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

    @staticmethod
    def get_current_date_time() -> str:
        """
        Returns the current date and time in ISO 8601 format with milliseconds.

        Examples:
            >>> from cafex_core.utils.date_time_utils import DateTimeActions
            >>> DateTimeActions().get_current_date_time()

        Returns:
            str: The current date and time in ISO 8601 format with milliseconds.
        """
        return (datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def get_time_by_zone(self, time_zone: str) -> datetime:
        """
        Fetches the current time in a specified timezone.

        This method takes a timezone string and returns the current time in that timezone.

        Examples:
            >>> from cafex_core.utils.date_time_utils import DateTimeActions
            >>> DateTimeActions().get_time_by_zone("America/New_York")

        Args:
            time_zone (str): The timezone for which the current time is to be fetched.

        Returns:
            datetime: The current time in the specified timezone.

        Raises:
            Exception: If there is an error in fetching the current time in the specified timezone.
        """
        try:
            # Get current UTC time using the timezone module
            date_utc_now = datetime.now(timezone.utc)

            # Convert to the specified timezone
            date_now_tz = date_utc_now.astimezone(pytz.timezone(time_zone))
            return date_now_tz
        except Exception as e:
            custom_exception_message = (
                "Exception in fetching today in given timezone. " f"Exception Details: {repr(e)}"
            )
            self.logger.exception(custom_exception_message)
            raise custom_exception_message from e

    def get_time_difference_seconds(self, end_time: str, start_time: str) -> float:
        """
        Returns the time difference in seconds between two times.

        Args:
            end_time (str): the end time in ISO 8601 format.
            start_time (str): The start time in ISO 8601 format.

        Returns:
            float: The time difference in seconds with millisecond precision.

        Raises:
            Exception: If there is an error in calculating the time difference.

        Examples:
            >>> from cafex_core.utils.date_time_utils import DateTimeActions
            >>> DateTimeActions().get_time_difference_seconds('2025-03-04T18:29:01.295',
            '2025-03-04T18:21:01.287')
        """
        try:
            end_dt = parser.parse(str(end_time))
            start_dt = parser.parse(str(start_time))

            # Use total_seconds() to get float with millisecond precision
            return (end_dt - start_dt).total_seconds()
        except Exception as e:
            self.logger.error("Error in get_time_difference_seconds--> %s", str(e))
            raise e

    def seconds_to_human_readable(self, seconds: float) -> str:
        """
        Converts seconds to a human-readable format.

        Args:
            seconds (float): The number of seconds.

        Returns:
            str: A human-readable string representing the duration.

        Raises:
            Exception: If there is an error in converting seconds to a human-readable format.

        Examples:
            >>> from cafex_core.utils.date_time_utils import DateTimeActions
            >>> DateTimeActions().seconds_to_human_readable(3661)
            >>> DateTimeActions().seconds_to_human_readable(0.145)
        """
        try:
            # Extract the whole seconds and milliseconds
            whole_seconds = int(seconds)
            milliseconds = int((seconds - whole_seconds) * 1000)

            # For very short durations (less than a second)
            if whole_seconds == 0:
                return f"{milliseconds} millisecond{'s' if milliseconds != 1 else ''}"

            # For durations with minutes
            minutes, secs = divmod(whole_seconds, 60)
            if minutes > 0:
                if hours := minutes // 60:
                    minutes %= 60
                    if days := hours // 24:
                        hours %= 24
                        result = f"{days} day{'s' if days != 1 else ''}"
                        if hours > 0:
                            result += f", {hours} hour{'s' if hours != 1 else ''}"
                        if minutes > 0:
                            result += f", {minutes} minute{'s' if minutes != 1 else ''}"
                        if secs > 0:
                            result += f", {secs} second{'s' if secs != 1 else ''}"
                    else:
                        result = f"{hours} hour{'s' if hours != 1 else ''}"
                        if minutes > 0:
                            result += f", {minutes} minute{'s' if minutes != 1 else ''}"
                        if secs > 0:
                            result += f", {secs} second{'s' if secs != 1 else ''}"
                else:
                    result = f"{minutes} minute{'s' if minutes != 1 else ''}"
                    if secs > 0:
                        result += f", {secs} second{'s' if secs != 1 else ''}"

                # Add milliseconds if present
                if milliseconds > 0:
                    result += f", {milliseconds} millisecond{'s' if milliseconds != 1 else ''}"
                return result

            # For durations with whole seconds and milliseconds
            if milliseconds > 0:
                seconds_str = f"{whole_seconds} second{'s' if whole_seconds != 1 else ''}"
                ms_str = f"{milliseconds} millisecond{'s' if milliseconds != 1 else ''}"
                return f"{seconds_str}, {ms_str}"

            # For durations with only whole seconds
            return f"{whole_seconds} second{'s' if whole_seconds != 1 else ''}"

        except Exception as e:
            self.logger.error("Error in seconds_to_human_readable--> %s", str(e))
            raise e
