from collections import UserDict
from functools import partial
from typing import Any, List

from flowmapper.context import ContextField
from flowmapper.string_field import StringField
from flowmapper.unit import UnitField

ATTRIBUTE_MAPPING = {
    "unit": partial(UnitField, use_lowercase=True),
    "context": ContextField,
    "identifier": partial(StringField, use_lowercase=True),
}


class ComparableFlowMapping(UserDict):
    def __init__(self, initialdata: dict):
        self.data = {
            key: ATTRIBUTE_MAPPING.get(key, StringField)(value)
            for key, value in initialdata.items()
        }

    def __setitem__(self, key: Any, value: Any) -> None:
        self.data[key] = ATTRIBUTE_MAPPING.get(key, StringField)(value)

    def __eq__(self, other: Any) -> bool:
        return all(value == other.get(key) for key, value in self.data.items() if value)


def prepare_transformations(transformations: List[dict] | None) -> List[dict]:
    if not transformations:
        return []

    prepared_transformations = []

    for transformation_dataset in transformations:
        for transformation_mapping in transformation_dataset.get("update", []):
            transformation_mapping["source"] = ComparableFlowMapping(
                transformation_mapping["source"]
            )
            for other_dataset in prepared_transformations:
                for other_mapping in other_dataset.get("update", []):
                    if other_mapping["source"] == transformation_mapping["source"]:
                        for key, value in other_mapping["target"].items():
                            transformation_mapping["source"][key] = value
                        break

        prepared_transformations.append(transformation_dataset)

    return prepared_transformations
