from typing import Any
import re
from collections import UserString
from functools import cached_property

valid_cas = re.compile(r"^\s*[0-9]{2,7}-[0-9]{2}-[0-9]{1}\s*$")


class CASField(UserString):
    def __init__(self, string: str):
        if not isinstance(string, (str, UserString)):
            raise TypeError(
                f"CASField takes only `str`, but got {type(string)} for {string}"
            )
        if not valid_cas.search(str(string)):
            raise ValueError(f"Given input is not valid CAS formatting: '{string}'")
        super().__init__(str(string))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CASField):
            return self.data == other.data
        elif isinstance(other, (str, UserString)):
            other_cas = CASField.from_string(str(other))
            if other_cas is None:
                return False
            return self.data == other_cas.data
        return False

    @staticmethod
    def from_string(string: str | None) -> "CASField | None":
        """Returns `None` if CAS number is invalid"""
        if string is None or not isinstance(string, (str, UserString)):
            return None
        new_cas = CASField(string.strip().lstrip("0").strip())
        if not new_cas.valid():
            return None
        return new_cas

    @property
    def digits(self) -> list[int]:
        return [int(d) for d in self.data.replace("-", "")]

    def export(self):
        return "{}-{}-{}".format(
            "".join([str(x) for x in self.digits[:-3]]),
            "".join([str(x) for x in self.digits[-3:-1]]),
            self.digits[-1],
        )

    @cached_property
    def check_digit_expected(self):
        """
        Expected digit acording to https://www.cas.org/support/documentation/chemical-substances/checkdig algorithm
        """
        result = (
            sum(
                [
                    index * value
                    for index, value in enumerate(self.digits[-2::-1], start=1)
                ]
            )
            % 10
        )
        return result

    def valid(self):
        return (self.digits[-1] == self.check_digit_expected) and bool(
            valid_cas.search(self.data)
        )
