from functools import cached_property


class CASField:
    """
    Class for CAS Registry Numbers that accepts padded or non-padded strings
    """

    def __init__(self, cas: str | None):
        if not isinstance(cas, str) and cas is not None:
            raise TypeError(f"cas should be a str, not {type(cas).__name__}")
        else:
            self.original = cas
            self.transformed = ("" if cas is None else cas).strip().lstrip("0").strip()
            self.digits = tuple(int(d) for d in self.transformed.replace("-", ""))

    @property
    def export(self):
        if self.original:
            return "{}-{}-{}".format(
                "".join([str(x) for x in self.digits[:-3]]),
                "".join([str(x) for x in self.digits[-3:-1]]),
                self.digits[-1],
            )
        else:
            return ""

    def __repr__(self):
        if not self.original:
            return "CASField with missing original value"
        else:
            return "{} CASField: '{}' -> '{}'".format(
                "Valid" if self.valid else "Invalid", self.original, self.export
            )

    def __eq__(self, other):
        if isinstance(other, CASField):
            return self.original and self.digits == other.digits
        if isinstance(other, str):
            try:
                return self.digits == CASField(other).digits
            except (TypeError, ValueError):
                return False
        return False

    @cached_property
    def check_digit_expected(self):
        """
        Expected digit acording to https://www.cas.org/support/documentation/chemical-substances/checkdig algorithm
        """
        result = (
            sum(
                [
                    index * value
                    for index, value in enumerate(self.digits[::-1], start=1)
                ]
            )
            % 10
        )
        return result

    @property
    def valid(self):
        """
        True if check if CAS number is valid acording to https://www.cas.org/support/documentation/chemical-substances/checkdig algorithm
        """
        return self.digits[-1] == self.check_digit_expected
