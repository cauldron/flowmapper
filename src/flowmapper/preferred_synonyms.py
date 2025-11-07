import re

from flowmapper.flow import Flow

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
    s: Flow, t: Flow, all_source_flows: list[Flow], all_target_flows: list[Flow], comment: str = "Identical preferred synonyms"
):
    if t.synonyms and s.name in t.synonyms and s.context == t.context:
        if s.name.normalized in t.name.normalized and (
            has_roman_numeral_at_end(t.name.normalized)
            or has_number_pattern_at_end(t.name.normalized)
        ):
            return {"comment": comment}
    elif s.synonyms and t.name in s.synonyms and s.context == t.context:
        if t.name.normalized in s.name.normalized and (
            has_roman_numeral_at_end(s.name.normalized)
            or has_number_pattern_at_end(s.name.normalized)
        ):
            return {"comment": comment}


def match_identical_names_in_synonyms(
    s: Flow, t: Flow, all_source_flows: list[Flow], all_target_flows: list[Flow], comment: str = "Identical synonyms"
):
    if (t.synonyms and s.name in t.synonyms and s.context == t.context) or (
        s.synonyms and t.name in s.synonyms and s.context == t.context
    ):
        return {"comment": comment}
