from typing import Any, Generic, TypeVar, Self

from flowmapper.utils import normalize_str

SF = TypeVar("SF")


class StringField(Generic[SF]):
    def __init__(
        self,
        value: str,
        use_lowercase: bool = True,
    ):
        self.value = value
        self.use_lowercase = use_lowercase

    def normalize(self) -> Self:
        value = normalize_str(self.value)
        if self.use_lowercase:
            value = value.lower()
        return StringField(value)

    def __eq__(self, other: Any) -> bool:
        if self.value == "":
            return False
        elif isinstance(other, StringField):
            return (
                self.value == other.value
            )
        elif isinstance(other, str):
            if self.use_lowercase:
                return self.value == normalize_str(other).lower()
            else:
                return self.value == normalize_str(other)
        else:
            return False

    def __bool__(self) -> bool:
        return bool(self.value)

    def __repr__(self) -> str:
        if not self.value:
            return "StringField with missing value"
        else:
            return f"StringField: '{self.value}'"
