from collections.abc import Collection, Iterator
from typing import Any

from flowmapper.string_field import StringField


class StringList(Collection):
    def __init__(self, strings: list[StringField | str]):
        self.strings = [StringField(s) if not isinstance(s, StringField) else s for s in strings]

    def __contains__(self, obj: Any) -> bool:
        return any(obj == elem for elem in self.strings)

    def __iter__(self) -> Iterator:
        yield from self.strings

    def __len__(self) -> int:
        return len(self.strings)

    def __bool__(self) -> bool:
        return bool(self.strings)

    def __repr__(self):
        if self:
            return f"StringList: {[repr(o) for o in self.strings]}"
        else:
            return "StringList: Empty"
