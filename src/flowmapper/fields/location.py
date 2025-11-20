"""
Location code extraction and manipulation utilities.

This module provides functions for working with location codes that appear as
suffixes in flow names. Location codes are typically appended to flow names
in the format ", <location>" where location is a recognized location code
from the places.json data file.

The module uses a compiled regex pattern (ends_with_location) to identify
location codes at the end of strings, following the pattern of a comma,
whitespace, and a recognized location code.
"""

import importlib.resources as resource
import json
import re
from pathlib import Path

import structlog

logger = structlog.get_logger("flowmapper")

RESULTS_DIR = Path(__file__).parent.parent / "manual_matching" / "results"

with resource.as_file(
    resource.files("flowmapper") / "data" / "places.json"
) as filepath:
    places = json.load(open(filepath))

# Compiled regex pattern that matches location codes at the end of strings.
# Pattern matches: comma (not preceded by whitespace), one or more spaces,
# followed by a recognized location code from places.json, optionally followed
# by whitespace, at the end of the string.
# The location code is captured in a named group "location".
ends_with_location = re.compile(
    r"(?<!\s),\s+(?P<location>{})\s*$".format(
        "|".join([re.escape(string) for string in places])
    ),
)
# All solutions I found for returning original string instead of
# lower case one were very ugly
# location_reverser = {obj.lower(): obj for obj in places}
# if len(location_reverser) != len(places):
#     raise ValueError("Multiple possible locations after lower case conversion")


# us_lci_ends_with_location = re.compile(
#     "/(?P<location>{})$".format(
#         "|".join(
#             [
#                 re.escape(string)
#                 for string in places
#                 if 2 <= len(string) <= 3 and string.upper() == string
#             ]
#         )
#     ),
# )

with resource.as_file(
    resource.files("flowmapper") / "data" / "names_and_locations.json"
) as filepath:
    names_and_locations = {o["source"]: o for o in json.load(open(filepath))}


def split_location_suffix(string: str) -> tuple[str, str | None]:
    """
    Split a string into name and location code if a location suffix is present.

    This function searches for a location code at the end of the input string
    using the ends_with_location regex pattern. If found, it returns the name
    part (without the location suffix) and the location code. If no location
    is found, it returns the original string and None.

    The location code must appear at the end of the string in the format
    ", <location>" where the comma is not preceded by whitespace, followed
    by one or more spaces, and then a recognized location code.

    Parameters
    ----------
    string : str
        The input string that may contain a location suffix at the end.

    Returns
    -------
    tuple[str, str | None]
        A tuple containing:
        - The name part without the location suffix (or original string if no
          location found)
        - The location code if found, otherwise None

    Examples
    --------
    >>> split_location_suffix("Ammonia, NL")
    ('Ammonia', 'NL')
    >>> split_location_suffix("Ammonia, pure, NL")
    ('Ammonia, pure', 'NL')
    >>> split_location_suffix("Ammonia")
    ('Ammonia', None)
    >>> split_location_suffix("Ammonia, NL, pure")
    ('Ammonia, NL, pure', None)
    >>> split_location_suffix(", NL")
    ('', 'NL')
    """
    if match := ends_with_location.search(string):
        return string[: match.start()], match.group("location")
    return string, None


def replace_location_suffix(string: str, new_location: str) -> str:
    """
    Replace the location value found by ends_with_location regex with a new value.

    If the string ends with a location code (matched by ends_with_location regex),
    replace it with the new location value. If no location is found, raises
    ValueError.

    Parameters
    ----------
    string : str
        The input string that must contain a location suffix at the end.
    new_location : str
        The new location value to replace the existing location with.

    Returns
    -------
    str
        The string with the location replaced.

    Raises
    ------
    ValueError
        If no location suffix is found in the input string.

    Examples
    --------
    >>> replace_location_suffix("Ammonia, NL", "DE")
    'Ammonia, DE'
    >>> replace_location_suffix("Ammonia, pure, NL", "FR")
    'Ammonia, pure, FR'
    >>> replace_location_suffix("Ammonia", "DE")
    Traceback (most recent call last):
        ...
    ValueError: No location suffix found in string 'Ammonia'
    """
    if match := ends_with_location.search(string):
        return (
            string[: match.start("location")]
            + new_location
            + string[match.end("location") :]
        )
    raise ValueError(f"No location suffix found in string {string!r}")
