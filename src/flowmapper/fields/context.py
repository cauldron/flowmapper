from collections.abc import Iterable
from typing import Any, Self

from flowmapper.utils import as_normalized_tuple

RESOURCE_CATEGORY = {
    "natural resources",
    "natural resource",
    "resources",
    "resource",
    "land use",
    "economic",
    "social",
    "raw materials",
    "raw",
}


class ContextField:
    def __init__(self, value: str | list[str] | tuple[str]):
        self.value = value

    def normalize(self, obj: Any | None = None, mapping: dict | None = None) -> Self:
        return type(self)(value=as_normalized_tuple(value=obj or self.value))

    def is_resource(self) -> bool:
        if isinstance(self.value, str):
            return any(cat in self.value.lower() for cat in RESOURCE_CATEGORY)
        else:
            lowered = [elem.lower() for elem in self.value]
            return any(cat in lowered for cat in RESOURCE_CATEGORY)

    def as_tuple(self) -> tuple | str:
        if isinstance(self.value, str):
            return self.value
        return tuple(self.value)

    def export_as_string(self, join_character: str = "✂️"):
        if isinstance(self.value, (list, tuple)):
            return join_character.join(self.value)
        return self.value

    def __iter__(self) -> Iterable:
        return iter(self.value)

    def __eq__(self, other: Any) -> bool:
        if self and other and isinstance(other, ContextField):
            return self.value == other.value
        else:
            try:
                return self.value == self.normalize(other).value
            except ValueError:
                return False

    def __repr__(self) -> str:
        return str(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __contains__(self, other: Any) -> bool:
        """`self` context is more generic than the `other` context.

        ```python
        Context("a/b") in Context("a/b/c")
        >>> True
        ```

        """
        if not isinstance(other, ContextField):
            return False
        return self.value == other.value[: len(self.value)]
