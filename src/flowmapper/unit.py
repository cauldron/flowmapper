import importlib.resources as resource
import math
from typing import Any, Generic, TypeVar

from pint import UnitRegistry, errors

from flowmapper.constants import PINT_MAPPING
from flowmapper.utils import normalize_str

ureg = UnitRegistry()

with resource.as_file(resource.files("flowmapper") / "data" / "units.txt") as filepath:
    ureg.load_definitions(filepath)

U = TypeVar("U")


class UnitField(Generic[U]):
    def __init__(
        self, original: str, transformed: str | None = None, use_lowercase: bool = False
    ):
        if transformed is None:
            transformed = original
        self.original = original
        if self.is_uri(transformed):
            # Private attribute, could change in future
            self._glossary_entry = self.resolve_uri(transformed)
            self.normalized = normalize_str(self._glossary_entry["label"])
        else:
            self.normalized = normalize_str(transformed)

        self.use_lowercase = use_lowercase
        if self.use_lowercase:
            self.normalized = self.normalized.lower()

        # Private attribute, could change in future
        self._pint_compatible = PINT_MAPPING.get(self.normalized, self.normalized)

    def is_uri(self, value: str) -> bool:
        # Placeholder for when we support glossary entries
        return False

    def resolve_uri(self, uri: str) -> None:
        # Placeholder
        pass

    def __repr__(self) -> str:
        return f"UnitField: '{self.original}' -> '{self.normalized}'"

    def __bool__(self) -> bool:
        return bool(self.original)

    def __eq__(self, other: Any):
        if isinstance(other, UnitField):
            return (
                self.normalized == other.normalized
                or self.conversion_factor(other) == 1
            )
        elif isinstance(other, str) and self.use_lowercase:
            return self.normalized == other.lower()
        elif isinstance(other, str):
            return self.normalized == other
        else:
            return False

    def compatible(self, other: Any):
        if not isinstance(other, UnitField):
            return False
        else:
            return math.isfinite(self.conversion_factor(other))

    def conversion_factor(self, to: U | Any) -> float:
        if not isinstance(to, UnitField):
            result = float("nan")
        elif isinstance(to, UnitField) and self.normalized == to.normalized:
            result = 1.0
        else:
            try:
                result = (
                    ureg(self._pint_compatible).to(ureg(to._pint_compatible)).magnitude
                )
            except (errors.DimensionalityError, errors.UndefinedUnitError):
                result = float("nan")
        return result
