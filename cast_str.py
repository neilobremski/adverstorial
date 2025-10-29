"""Helper functions to cast strings to other types."""
import re

def to_bool(value, default=False):
    if type(value) is bool:
        return value
    if value is None or value == '':
        return default
    if value.lower() in ['true', 'yes', '1', 'on']:
        return True
    return False

def to_float(value, default=0.0):
    if type(value) is float:
        return value
    if value is None or value == '':
        return default
    try:
        return float(value)
    except ValueError:
        return default

def to_int(value, default=0):
    if type(value) is int:
        return value
    if value is None or value == '':
        return default
    return int(value)

def to_list(value, separator=None, default=None):
    """Coerce (string) value into a list.
    :param separator: Optional separator to split the string. May be a string or regex.
    :param default: Default value to return if the input is None or empty.
    :return: List of strings.
    """
    if type(value) is list:
        return value
    if value is None or value == '':
        return default
    if separator is None:  # default to /[\s,;]+/
        separator = re.compile(r'[\s,;]+')
    if isinstance(separator, re.Pattern):
        return separator.split(str(value))
    return str(value).split(separator)
