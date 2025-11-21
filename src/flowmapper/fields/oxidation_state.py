import re
from typing import Any, Self

import roman

roman_numberals_optional_parentheses = re.compile(
    r"[\,\s]+\(?\s*(?P<numeral>[IVX]+)\s*(?P<sign>[+-]*)\)?\s*$",
    flags=re.IGNORECASE,
)
numbers_optional_parentheses = re.compile(
    r"[\,\s]+\(?\s*(?P<sign>[+-]+)(?P<numeral>[0-9]+)\)?\s*$"
)


class OxidationState:
    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, OxidationState):
            return self.value == other.value
        else:
            return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    @staticmethod
    def has_oxidation_state(obj: str) -> bool:
        return roman_numberals_optional_parentheses.search(
            obj
        ) or numbers_optional_parentheses.search(obj)

    @classmethod
    def from_string(cls, obj: str) -> tuple[Self, str]:
        if match := roman_numberals_optional_parentheses.search(obj):
            obj_dict = match.groupdict()
            try:
                value = roman.fromRoman(obj_dict["numeral"].upper())
            except roman.InvalidRomanNumeralError:
                raise ValueError(
                    f"{obj_dict['numeral']} in string {obj} is not a valid roman numeral"
                )
            if "-" in obj_dict["sign"]:
                value *= -1
        elif match := numbers_optional_parentheses.search(obj):
            obj_dict = match.groupdict()
            value = eval(obj_dict["numeral"].lstrip("0"))
            if "-" in obj_dict["sign"]:
                value *= -1
        else:
            raise ValueError("No match found")

        if value < -5 or value > 9:
            raise ValueError(
                f"Oxidation state {value} from name {obj} is outside physical bounds of [-5, +9]"
            )

        return OxidationState(value), obj[: match.start()]
