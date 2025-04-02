"""
This module contains regular expressions and constants used for string manipulation.
"""
import re

# File name sanitization
INVALID_FILENAME_CHARS = r'\\[]<>:?*|"\'\/'
URL_SPECIAL_CHARS = r"[=&#+]"  # Characters commonly found in URLs
DATETIME_CHARS = r"[-\s+:.]"  # Characters to remove from timestamps

# Step name cleaning
STEP_NAME_WHITESPACE = r"[ \n\t|]"  # Whitespace in step names
MULTIPLE_WHITESPACE = r"\s+"  # Multiple whitespace characters

# Screenshot name cleaning
SCREENSHOT_NAME_REPLACE = r"[ \n\t|]"  # Characters to replace in screenshot names
MULTIPLE_UNDERSCORE = r"_+"  # Multiple underscores

# Trace analysis patterns
TRACE_ORIGIN = r"in (\w+) \[(\w+)\]"  # Method and class name from stack trace

# Compile the regular expressions for better performance
INVALID_FILENAME_CHARS_PATTERN = re.compile(f"[{re.escape(INVALID_FILENAME_CHARS)}]")
URL_SPECIAL_CHARS_PATTERN = re.compile(URL_SPECIAL_CHARS)
DATETIME_CHARS_PATTERN = re.compile(DATETIME_CHARS)
STEP_NAME_WHITESPACE_PATTERN = re.compile(STEP_NAME_WHITESPACE)
MULTIPLE_WHITESPACE_PATTERN = re.compile(MULTIPLE_WHITESPACE)
SCREENSHOT_NAME_REPLACE_PATTERN = re.compile(SCREENSHOT_NAME_REPLACE)
MULTIPLE_UNDERSCORE_PATTERN = re.compile(MULTIPLE_UNDERSCORE)
TRACE_ORIGIN_PATTERN = re.compile(TRACE_ORIGIN)

# Constants for length limits
MAX_SCREENSHOT_NAME_LENGTH = 100  # Maximum length for screenshot base names
