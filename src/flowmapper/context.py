from typing import Self, Any


MISSING_VALUES = {
    "",
    "(unknown)",
    "(unspecified)",
    "null",
    "unknown",
    "unspecified",
}


class ContextField:
    def __init__(self, value: str | list[str] | tuple[str]):
        self.value = value

    def normalize(self, obj: Any | None = None, mapping: dict | None = None) -> Self:
        value = obj or self.value
        if isinstance(value, (tuple, list)):
            intermediate = list(value)
        elif isinstance(value, str) and "/" in value:
            intermediate = list(value.split("/"))
        elif isinstance(value, str):
            intermediate = [value]
        else:
            raise ValueError(f"Can't understand input context {self.value}")

        intermediate = [elem.lower().strip() for elem in intermediate]

        while intermediate[-1] in MISSING_VALUES:
            intermediate = intermediate[:-1]

        # TODO: Apply mapping

        return type(self)(value=tuple(intermediate))

    def export_as_string(self, join_character: str = "✂️"):
        if isinstance(self.value, (list, tuple)):
            return join_character.join(self.value)
        return self.value

    def __iter__(self):
        return iter(self.value)

    def __eq__(self, other: Any) -> bool:
        if self and other and isinstance(other, ContextField):
            return self.value == other.value
        else:
            try:
                return self.value == self.normalize(other).value
            except ValueError:
                return False

    def __repr__(self):
        return f"ContextField: {self.value}"

    def __bool__(self):
        return bool(self.value)

    def __hash__(self):
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
