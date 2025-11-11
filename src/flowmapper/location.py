import importlib.resources as resource
import json
import re
from pathlib import Path

import structlog

logger = structlog.get_logger("flowmapper")

RESULTS_DIR = Path(__file__).parent / "manual_matching" / "results"

with resource.as_file(
    resource.files("flowmapper") / "data" / "places.json"
) as filepath:
    places = json.load(open(filepath))

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
    if match := ends_with_location.search(string):
        return string[: match.start()], match.group("location")
    return string, None
