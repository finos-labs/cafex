import unittest
import logging
from cafex_core.logging.colargulog import ColorCodes, ColorizedArgsFormatter, BraceFormatStyleFormatter


class TestColorCodes(unittest.TestCase):
    def test_color_codes(self):
        self.assertEqual(ColorCodes.grey, "\x1b[38;21m")
        self.assertEqual(ColorCodes.green, "\x1b[1;32m")
        self.assertEqual(ColorCodes.yellow, "\x1b[33;21m")
        self.assertEqual(ColorCodes.red, "\x1b[31;21m")
        self.assertEqual(ColorCodes.bold_red, "\x1b[31;1m")
        self.assertEqual(ColorCodes.blue, "\x1b[1;34m")
        self.assertEqual(ColorCodes.light_blue, "\x1b[1;36m")
        self.assertEqual(ColorCodes.purple, "\x1b[1;35m")
        self.assertEqual(ColorCodes.reset, "\x1b[0m")


class TestColorizedArgsFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = ColorizedArgsFormatter("%(levelname)s: %(message)s")

    def test_format_debug(self):
        record = logging.LogRecord(name="test", level=logging.DEBUG, pathname="", lineno=0, msg="Debug message",
                                   args=(), exc_info=None)
        formatted = self.formatter.format(record)
        self.assertIn(ColorCodes.grey, formatted)
        self.assertIn(ColorCodes.reset, formatted)

    def test_format_info(self):
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Info message", args=(),
                                   exc_info=None)
        formatted = self.formatter.format(record)
        self.assertIn(ColorCodes.green, formatted)
        self.assertIn(ColorCodes.reset, formatted)

    def test_format_warning(self):
        record = logging.LogRecord(name="test", level=logging.WARNING, pathname="", lineno=0, msg="Warning message",
                                   args=(), exc_info=None)
        formatted = self.formatter.format(record)
        self.assertIn(ColorCodes.yellow, formatted)
        self.assertIn(ColorCodes.reset, formatted)

    def test_format_error(self):
        record = logging.LogRecord(name="test", level=logging.ERROR, pathname="", lineno=0, msg="Error message",
                                   args=(), exc_info=None)
        formatted = self.formatter.format(record)
        self.assertIn(ColorCodes.red, formatted)
        self.assertIn(ColorCodes.reset, formatted)

    def test_format_critical(self):
        record = logging.LogRecord(name="test", level=logging.CRITICAL, pathname="", lineno=0, msg="Critical message",
                                   args=(), exc_info=None)
        formatted = self.formatter.format(record)
        self.assertIn(ColorCodes.bold_red, formatted)
        self.assertIn(ColorCodes.reset, formatted)

    def test_rewrite_record(self):
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with {0}",
                                   args=("arg",), exc_info=None)
        ColorizedArgsFormatter.rewrite_record(record)
        self.assertEqual(record.msg, "Message with \x1b[1;35marg\x1b[0m")


class TestBraceFormatStyleFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = BraceFormatStyleFormatter("%(levelname)s: %(message)s")

    def test_is_brace_format_style(self):
        # Test case where "%" is in the message
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with %s", args=("arg",), exc_info=None)
        self.assertFalse(BraceFormatStyleFormatter.is_brace_format_style(record))

        # Test case where count of "{" and "}" are not equal
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with {", args=("arg",), exc_info=None)
        self.assertFalse(BraceFormatStyleFormatter.is_brace_format_style(record))

        # Test case where count of "{" does not match the number of arguments
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with {}", args=(), exc_info=None)
        self.assertFalse(BraceFormatStyleFormatter.is_brace_format_style(record))

        # Test case to cover the final return False
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with no braces", args=("arg",), exc_info=None)
        self.assertFalse(BraceFormatStyleFormatter.is_brace_format_style(record))

    def test_rewrite_record(self):
        # Test case to cover the return statement
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with %s", args=("arg",), exc_info=None)
        BraceFormatStyleFormatter.rewrite_record(record)
        self.assertEqual(record.msg, "Message with %s")

        # Test case where the record is rewritten
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with {}", args=("arg",), exc_info=None)
        BraceFormatStyleFormatter.rewrite_record(record)
        self.assertEqual(record.msg, "Message with arg")

    def test_format(self):
        record = logging.LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="Message with {}",
                                   args=("arg",), exc_info=None)
        formatted = self.formatter.format(record)
        self.assertEqual(formatted, "INFO: Message with arg")


if __name__ == "__main__":
    unittest.main()
