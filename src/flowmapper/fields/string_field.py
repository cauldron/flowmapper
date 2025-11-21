from collections import UserString
from typing import Any, Self

from flowmapper.utils import normalize_str


class StringField(UserString):
    def normalize(self, lowercase: bool = True) -> Self:
        value = normalize_str(self.data)
        if lowercase:
            value = value.lower()
        return type(self)(value)

    def __eq__(self, other: Any) -> bool:
        if not self.data:
            # Empty strings aren't equal for our use case
            return False
        elif isinstance(other, StringField):
            return self.data == other.data
        elif isinstance(other, str):
            return self.data == other or self.data == normalize_str(other)
        else:
            return False
