import importlib.resources as resource
import json
import math
from collections import UserString
from pathlib import Path
from typing import Any, Self

from pint import UnitRegistry, errors

from flowmapper.utils import normalize_str

ureg = UnitRegistry()

with resource.as_file(resource.files("flowmapper") / "data" / "units.txt") as filepath:
    ureg.load_definitions(filepath)

with open(Path(__file__).parent / "data" / "standard-units-harmonization.json") as f:
    UNIT_MAPPING = {
        line["source"]["unit"]: line["target"]["unit"]
        for line in json.load(f)["update"]
    }


class UnitField(UserString):
    def normalize(self) -> Self:
        """Normalize string to fit into our `pint` definitions"""
        label = normalize_str(self.data)
        if label in UNIT_MAPPING:
            label = UNIT_MAPPING[label]
        try:
            ureg(label)
        except errors.UndefinedUnitError:
            raise ValueError(
                f"Unit {label} is unknown; add to flowmapper `units.txt` or define a mapping in `unit-mapping.json`"
            )
        # Makes type checkers happy, if inelegant...
        return type(self)(label)

    def is_uri(self, value: str) -> bool:
        # Placeholder for when we support glossary entries
        return False

    def resolve_uri(self, uri: str) -> None:
        # Placeholder
        pass

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UnitField):
            return self.data == other.data or self.conversion_factor(other) == 1
        else:
            return self.data == other

    def compatible(self, other: Any) -> bool:
        return math.isfinite(self.conversion_factor(other))

    def conversion_factor(self, to: Any) -> float:
        if not isinstance(to, (UnitField, str)):
            result = float("nan")
        elif isinstance(to, UnitField) and self.data == to.data:
            result = 1.0
        else:
            try:
                result = ureg(self.data).to(ureg(str(to))).magnitude
            except (errors.DimensionalityError, errors.UndefinedUnitError):
                result = float("nan")
        return result
