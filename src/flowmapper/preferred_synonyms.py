import re

from flowmapper.domain import Flow

ROMAN_NUMERAL_PATTERN = re.compile(r"\b\(?[ivx]+[\+-]?\)?\s*$", flags=re.IGNORECASE)
PARENTHESES_PATTERN = re.compile(r"\([1-9]+[\+-]?\)\s*$")


def has_roman_numeral_at_end(text: str) -> bool:
    """
    Check if a string ends with a roman numeral.

    Args:
        text (str): The string to check

    Returns:
        bool: True if the string ends with a roman numeral, False otherwise

    """
    return bool(ROMAN_NUMERAL_PATTERN.search(text))


def has_number_pattern_at_end(text: str) -> bool:
    """
    Check if a string ends with a pattern like "(2+)".

    Args:
        text (str): The string to check

    Returns:
        bool: True if the string ends with the number pattern, False otherwise

    """
    return bool(PARENTHESES_PATTERN.search(text))


def match_identical_names_in_preferred_synonyms(
    source_flows: list[Flow],
    target_flows: list[Flow],
    comment: str = "Identical preferred synonyms",
):
    if t.synonyms and s.name in t.synonyms and s.context == t.context:
        if s.name.normalized in t.name.normalized and (
            has_roman_numeral_at_end(t.name.normalized)
            or has_number_pattern_at_end(t.name.normalized)
        ):
            # Check if there's another target flow with a different name that shares the same synonym
            for other_target in all_target_flows:
                if (
                    other_target is not t
                    and other_target.name.normalized != t.name.normalized
                    and other_target.synonyms
                    and s.name in other_target.synonyms
                    and other_target.context == s.context
                ):
                    return None
            return {"comment": comment}
    elif s.synonyms and t.name in s.synonyms and s.context == t.context:
        if t.name.normalized in s.name.normalized and (
            has_roman_numeral_at_end(s.name.normalized)
            or has_number_pattern_at_end(s.name.normalized)
        ):
            # Check if there's another target flow with a different name that shares the same synonym
            for other_target in all_target_flows:
                if (
                    other_target is not t
                    and other_target.name.normalized != t.name.normalized
                    and other_target.synonyms
                    and t.name in other_target.synonyms
                    and other_target.context == s.context
                ):
                    return None
            return {"comment": comment}


def match_identical_names_in_synonyms(
    source_flows: list[Flow],
    target_flows: list[Flow],
    comment: str = "Identical synonyms",
):
    if (t.synonyms and s.name in t.synonyms and s.context == t.context) or (
        s.synonyms and t.name in s.synonyms and s.context == t.context
    ):
        return {"comment": comment}
