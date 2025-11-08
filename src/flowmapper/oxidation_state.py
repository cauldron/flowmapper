from typing import Self, Any

import re
import roman

roman_numberals_optional_parentheses = re.compile(r"(?P<comma>\,?)\s*\(?\s*(?P<numeral>[IVX]+)\s*(?P<sign>[+-]*)\)?\s*$", flags=re.IGNORECASE)
numbers_optional_parentheses = re.compile(r"(?P<comma>\,?)\s*\(?\s*(?P<sign_before>[+-]?)(?P<numeral>[0-9]+)(?P<sign_after>[+-]?)\)?\s*$")

class OxidationState:
    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, OxidationState):
            return self.value == other.value
        else:
            return self.value == other

    @staticmethod
    def has_oxidation_state(obj: str) -> bool:
        return roman_numberals_optional_parentheses.search(obj) or numbers_optional_parentheses.search(obj)

    @classmethod
    def from_string(cls, obj: str) -> tuple[Self, str]:
        if (match := roman_numberals_optional_parentheses.search(obj)):
            obj_dict = match.groupdict()
            try:
                value = roman.fromRoman(obj_dict["numeral"].upper())
            except roman.InvalidRomanNumeralError:
                raise ValueError(f"{obj_dict['numeral']} in string {obj} is not a valid roman numeral")
            if "-" in obj_dict["sign"]:
                value *= -1
        elif match := numbers_optional_parentheses.search(obj):
            obj_dict = match.groupdict()
            if obj_dict["sign_before"] and obj_dict["sign_after"]:
                raise ValueError(f"Sign before and after the oxidation state number are not allowed: {obj}")

            value = eval(obj_dict["numeral"].lstrip('0'))
            if "-" in obj_dict["sign_before"] or "-" in obj_dict["sign_after"]:
                value *= -1
        else:
            raise ValueError("No match found")

        if value < -5 or value > 9:
            raise ValueError("Oxidation state outside [-5, +9] is physically impossible")

        return OxidationState(value), obj[:match.start()]
