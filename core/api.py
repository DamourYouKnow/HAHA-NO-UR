"""
A collection of useful functions.
"""
import re
from typing import List


def split_camel(s: str) -> List[str]:
    """
    Split a string by starting chars of UpperCamelCase
    :param s: the input string.
    :return: a list of strings that was split by capital letters.
    """
    regex = re.compile('[A-Z][^A-Z]*')
    return regex.findall(s)
