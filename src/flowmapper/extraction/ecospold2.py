import json
from collections import defaultdict
from pathlib import Path

import xmltodict


def reformat(obj: dict) -> dict:
    data = {
        "identifier": obj["@id"],
        "unit": obj["unitName"]["#text"],
        "context": [
            obj["compartment"]["compartment"]["#text"],
            obj["compartment"]["subcompartment"]["#text"],
        ],
        "name": obj["name"]["#text"],
    }
    if obj.get("synonym") and isinstance(obj["synonym"], list):
        data["synonyms"] = [s["#text"] for s in obj["synonym"] if "#text" in s]
    elif obj.get("synonym") and "#text" in obj["synonym"]:
        data["synonyms"] = [obj["synonym"]["#text"]]
    if "@casNumber" in obj:
        data["cas_number"] = obj["@casNumber"]
    return data


def remove_conflicting_synonyms(data: list[dict]) -> list[dict]:
    """
    Remove synonyms which conflict with the base names of other flows within the same category tree
    branch.

    For example, if flow `A` has a synonym `water` and a context `['ground']`, and flow `B` has the
    name `water` and the context `['ground', 'deep']`, then the synonym `water` would be removed
    from `A`. However, if `B` had the context `['something', 'else']`, then `water` would be kept,
    as it wouldn't directly overlap a different flow in the same category tree branch.
    """
    base_names = defaultdict(list)
    for obj in data:
        if obj.get("name") and obj.get("context"):
            base_names[obj["context"][0]].append(obj["name"].lower())

    for obj in data:
        if not (obj.get("synonyms") and obj.get("context")):
            continue
        obj["synonyms"] = [
            syn
            for syn in obj["synonyms"]
            if syn.lower() not in base_names[obj["context"][0]]
        ]

    return data


def ecospold2_biosphere_extractor(input_path: Path, output_path: Path) -> None:
    if not input_path.name == "ElementaryExchanges.xml":
        raise ValueError("`input_path` must be for a `ElementaryExchanges.xml` file")
    with open(input_path) as fs:
        ei_xml = xmltodict.parse(fs.read(), strip_whitespace=False)[
            "validElementaryExchanges"
        ]["elementaryExchange"]

    with open(output_path, "w") as fs:
        json.dump(
            remove_conflicting_synonyms([reformat(obj) for obj in ei_xml]), fs, indent=2
        )
    return True
