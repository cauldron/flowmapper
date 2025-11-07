from typing import Any, Generic, TypeVar

from flowmapper.utils import normalize_str

SF = TypeVar("SF")


class StringField(Generic[SF]):
    def __init__(
        self,
        original: str | None,
        transformed: str | None = None,
        use_lowercase: bool = True,
    ):
        self.original = original
        self.normalized = normalize_str(transformed or original)
        self.use_lowercase = use_lowercase
        if self.use_lowercase:
            self.normalized = self.normalized.lower()

    def __eq__(self, other: Any) -> bool:
        if self.normalized == "":
            return False
        elif isinstance(other, StringField):
            return (
                self.normalized == other.normalized or self.original == other.original
            )
        elif isinstance(other, str):
            if self.use_lowercase:
                return self.normalized == other.lower()
            else:
                return self.normalized == other
        else:
            return False

    def __bool__(self) -> bool:
        return bool(self.original)

    def __repr__(self) -> str:
        if not self.original:
            return "StringField with missing original value"
        else:
            return f"StringField: '{self.original}' -> '{self.normalized}'"
