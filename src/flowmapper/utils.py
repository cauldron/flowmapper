import copy
import hashlib
import importlib.resources as resource
import json
import re
import unicodedata
from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any, List, Union

RESULTS_DIR = Path(__file__).parent / "manual_matching" / "results"

with resource.as_file(
    resource.files("flowmapper") / "data" / "places.json"
) as filepath:
    places = json.load(open(filepath))

ends_with_location = re.compile(
    ",[ \t\r\f]+(?P<code>{})$".format(
        "|".join([re.escape(string) for string in places])
    ),
    re.IGNORECASE,
)
# All solutions I found for returning original string instead of
# lower case one were very ugly
location_reverser = {obj.lower(): obj for obj in places}
if len(location_reverser) != len(places):
    raise ValueError("Multiple possible locations after lower case conversion")

us_lci_ends_with_location = re.compile(
    "/(?P<location>{})$".format(
        "|".join(
            [
                re.escape(string)
                for string in places
                if 2 <= len(string) <= 3 and string.upper() == string
            ]
        )
    ),
)

with resource.as_file(
    resource.files("flowmapper") / "data" / "names_and_locations.json"
) as filepath:
    names_and_locations = {o["source"]: o for o in json.load(open(filepath))}


def load_standard_transformations() -> List:
    # with resource.as_file(
    #     resource.files("flowmapper") / "data" / "standard-units-harmonization.json"
    # ) as filepath:
    #     units = json.load(open(filepath))
    with resource.as_file(
        resource.files("flowmapper") / "data" / "simapro-2023-ecoinvent-3-contexts.json"
    ) as filepath:
        contexts = json.load(open(filepath))
    # return [units, contexts]
    return [contexts]


def generate_flow_id(flow: dict):
    flow_str = json.dumps(flow, sort_keys=True)
    result = hashlib.md5(flow_str.encode("utf-8")).hexdigest()
    return result


def read_migration_files(*filepaths: Union[str, Path]) -> List[dict]:
    """
    Read and aggregate migration data from multiple JSON files.

    This function opens and reads a series of JSON files, each containing migration data as a list of dicts without the change type.
    It aggregates all changes into a single list and returns it wrapped in a dictionary
    under the change type 'update'.

    Parameters
    ----------
    *filepaths : Path
        Variable length argument list of Path objects.

    Returns
    -------
    dict
        A dictionary containing a single key 'update', which maps to a list. This list is
        an aggregation of the data from all the JSON files read.
    """
    migration_data = []

    for filepath in filepaths:
        if (RESULTS_DIR / filepath).is_file():
            filepath = RESULTS_DIR / filepath
        with open(Path(filepath), "r") as fs:
            migration_data.append(json.load(fs))

    return migration_data


def rm_parentheses_roman_numerals(s: str):
    pattern = r"\(\s*([ivxlcdmIVXLCDM]+)\s*\)"
    return re.sub(pattern, r"\1", s, flags=re.IGNORECASE)


def rm_roman_numerals_ionic_state(s: str):
    pattern = r"\s*\(\s*[ivxlcdm]+\s*\)$"
    return re.sub(pattern, "", s)


def normalize_str(s):
    if s is not None:
        return unicodedata.normalize("NFC", s).strip()
    else:
        return ""


def transform_flow(flow, transformation):
    result = copy.copy(flow)
    result.update(transformation["target"])
    return result


def matcher(source, target):
    return all(target.get(key) == value for key, value in source.items())


def rowercase(obj: Any) -> Any:
    """Recursively transform everything to lower case recursively"""
    if isinstance(obj, str):
        return obj.lower()
    elif isinstance(obj, Mapping):
        return type(obj)([(rowercase(k), rowercase(v)) for k, v in obj.items()])
    elif isinstance(obj, Collection):
        return type(obj)([rowercase(o) for o in obj])
    else:
        return obj


def match_sort_order(obj: dict) -> tuple:
    return (
        not obj["from"].name,
        obj["from"].name.normalized,
        not obj["from"].context,
        obj["from"].context.export_as_string(),
    )


def apply_transformations(obj: dict, transformations: List[dict] | None) -> dict:
    if not transformations:
        return obj
    obj = copy.deepcopy(obj)
    lower = rowercase(obj)

    for dataset in transformations:
        for transformation_obj in dataset.get("create", []):
            if matcher(
                transformation_obj,
                lower if dataset.get("case-insensitive") else obj,
            ):
                # Marked an needs to be created; missing in target list
                obj["__missing__"] = True
                break
        for transformation_obj in dataset.get("update", []):
            if transformation_obj["source"] == obj:
                obj.update(transformation_obj["target"])
                if "conversion_factor" in transformation_obj:
                    obj["conversion_factor"] = transformation_obj["conversion_factor"]
                break

    return obj
