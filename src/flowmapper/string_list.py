from collections.abc import Collection, Iterable
from typing import Any, List

from flowmapper.string_field import StringField


class StringList(Collection):
    def __init__(self, original: List[str], transformed: List[str] | None = None):
        transformed = transformed or original
        if original is None:
            self.data = []
        else:
            self.data = [
                StringField(original=a, transformed=b)
                for a, b in zip(original, transformed)
            ]

    def __contains__(self, obj: Any) -> bool:
        return any(obj == elem for elem in self.data)

    def __iter__(self) -> Iterable:
        yield from self.data

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __repr__(self):
        if self:
            return "StringList: {}".format([repr(o) for o in self.data])
        else:
            return "StringList: Empty"
