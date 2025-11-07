import pytest

from flowmapper.flow import Flow
from flowmapper.preferred_synonyms import (
    has_number_pattern_at_end,
    has_roman_numeral_at_end,
    match_identical_names_in_preferred_synonyms,
)


@pytest.mark.parametrize(
    "text",
    [
        "Chapter I",
        "Section V",
        "Appendix XXI",
        "Book III",
        "Part IV",
        "Chapter VI",
        "Section VII",
        "Appendix VIII",
        "Appendix VIII+",
        "Appendix VIII-",
        "Appendix viii",
        "Book IX",
        "Part X",
        "Chapter XI",
        "Section XV",
        "Appendix XX",
        "Book XXX",
        "Chapter II ",  # Trailing space
        "  Chapter III  ",  # Leading and trailing spaces
        "Chapter (I)",  # With parentheses
        "Section (V+)",  # With parentheses and plus
        "Book (III-)",  # With parentheses and minus
    ],
)
def test_roman_numerals_should_match(text):
    """Test that valid roman numerals at the end of strings are detected."""
    assert has_roman_numeral_at_end(text), f"Expected has_roman_numeral_at_end('{text}') to return True, but it returned False"


@pytest.mark.parametrize(
    "text",
    [
        "Chapter 1",
        "Appendix VIII-+",
        "Section A",
        "Part XL",
        "Chapter L",
        "Appendix C",
        "Chapter DC",
        "Section M",
        "Part MMMCMXCIX",  # 3999
        "I am at the beginning",
        "This ends with I but not roman",
        "",
        "   ",
        "Chapter",
    ],
)
def test_non_roman_numerals_should_not_match(text):
    """Test that invalid or non-roman numerals are not detected."""
    assert not has_roman_numeral_at_end(text), f"Expected has_roman_numeral_at_end('{text}') to return False, but it returned True"


@pytest.mark.parametrize(
    "text",
    [
        "Substance (1+)",
        "Compound (2-)",
        "Element (3)",
        "Chemical (5+)",
        "Material (7-)",
        "Substance (9)",
        "Element (11)",  # Multi-digit numbers are allowed
        "Substance (1+) ",  # Trailing space
        "  Compound (2-)  ",  # Leading and trailing spaces
        "Element (123+)",  # Multiple digits with plus
        "Compound (456-)",  # Multiple digits with minus
    ],
)
def test_number_patterns_should_match(text):
    """Test that valid number patterns at the end of strings are detected."""
    assert has_number_pattern_at_end(text), f"Expected has_number_pattern_at_end('{text}') to return True, but it returned False"


@pytest.mark.parametrize(
    "text",
    [
        "Chemical",
        "Substance 1+",  # Missing parentheses
        "Molecule (1+2)",
        "Compound (0)",
        "Chemical ()",  # Empty parentheses
        "Material (+)",  # Just plus sign
        "Substance (-)",  # Just minus sign
        "Element (10)",
        "Substance 1-",  # Missing parentheses
        "Chemical (5+-)",
        "Substance 1-+",  # Missing parentheses
        "Molecule (1+2",  # Missing closing parenthesis
        "Element 1+2)",  # Missing opening parenthesis
        "Compound (1+2",  # Missing closing parenthesis
        "",
        "   ",
        "Substance (1+2) extra",  # Text after pattern
        "(1+) Substance",  # Pattern not at end
    ],
)
def test_invalid_patterns_should_not_match(text):
    """Test that invalid patterns are not detected."""
    assert not has_number_pattern_at_end(text), f"Expected has_number_pattern_at_end('{text}') to return False, but it returned True"


def test_match_when_target_has_source_name_in_synonyms_with_roman_numeral():
    """Test matching when target has source name in synonyms and target name ends with roman numeral."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",  # Ends with roman numeral
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_match_when_target_has_source_name_in_synonyms_with_number_pattern():
    """Test matching when target has source name in synonyms and target name ends with number pattern."""
    source_data = {
        "name": "carbon",
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["co2"],
    }
    target_data = {
        "name": "carbon (2+)",  # Ends with number pattern
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["carbon", "c"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_match_when_source_has_target_name_in_synonyms_with_roman_numeral():
    """Test matching when source has target name in synonyms and source name ends with roman numeral."""
    source_data = {
        "name": "nitrogen II",  # Ends with roman numeral
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["nitrogen", "n2"],
    }
    target_data = {
        "name": "nitrogen",
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["n2"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_match_when_source_has_target_name_in_synonyms_with_number_pattern():
    """Test matching when source has target name in synonyms and source name ends with number pattern."""
    source_data = {
        "name": "oxygen (1-)",  # Ends with number pattern
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["oxygen", "o2"],
    }
    target_data = {
        "name": "oxygen",
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["n2"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_no_match_when_different_contexts():
    """Test that no match occurs when contexts are different."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",
        "context": ["air"],  # Different context
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result is None, f"Expected result to be None, but got {result}"


def test_no_match_when_name_not_in_synonyms():
    """Test that no match occurs when name is not in synonyms."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["aqua", "liquid"],  # "water" not in synonyms
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result is None, f"Expected result to be None, but got {result}"


def test_no_match_when_no_roman_numeral_or_number_pattern():
    """Test that no match occurs when name doesn't end with roman numeral or number pattern."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water",  # No roman numeral or number pattern
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result is None, f"Expected result to be None, but got {result}"


def test_no_match_when_name_not_contained_in_other_name():
    """Test that no match occurs when one name is not contained in the other."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "different I",  # "water" not contained in "different_water I"
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result is None, f"Expected result to be None, but got {result}"


def test_no_match_when_no_synonyms():
    """Test that no match occurs when flows have no synonyms."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": [],  # No synonyms
    }
    target_data = {
        "name": "water I",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": [],  # No synonyms
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result is None, f"Expected result to be None, but got {result}"


def test_custom_comment():
    """Test that custom comment is returned when provided."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    custom_comment = "Custom match comment"
    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [], custom_comment
    )

    assert result == {"comment": custom_comment}, f"Expected result to be {{'comment': '{custom_comment}'}}, but got {result}"


def test_match_with_roman_numeral_and_plus_minus():
    """Test matching with roman numerals that have + or - signs."""
    source_data = {
        "name": "iron",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["fe"],
    }
    target_data = {
        "name": "iron II+",  # Roman numeral with plus
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["iron", "fe"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_match_with_number_pattern_and_plus_minus():
    """Test matching with number patterns that have + or - signs."""
    source_data = {
        "name": "sodium",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["na"],
    }
    target_data = {
        "name": "sodium (1+)",  # Number pattern with plus
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["sodium", "na"],
    }

    source = Flow(source_data)
    target = Flow(target_data)

    result = match_identical_names_in_preferred_synonyms(source, target, [], [])

    assert result == {"comment": "Identical preferred synonyms"}, f"Expected result to be {{'comment': 'Identical preferred synonyms'}}, but got {result}"


def test_no_match_when_another_target_shares_same_synonym_different_name():
    """Test that no match occurs when another target flow with a different name shares the same synonym."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",  # Ends with roman numeral
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }
    other_target_data = {
        "name": "water II",  # Different name, but also has "water" in synonyms
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "h2o"],
    }

    source = Flow(source_data)
    target = Flow(target_data)
    other_target = Flow(other_target_data)

    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [other_target]
    )

    assert result is None, f"Expected result to be None when another target shares the same synonym, but got {result}"


def test_no_match_when_another_target_shares_same_synonym_number_pattern():
    """Test that no match occurs when another target flow with a different name shares the same synonym (number pattern case)."""
    source_data = {
        "name": "carbon",
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["co2"],
    }
    target_data = {
        "name": "carbon (2+)",  # Ends with number pattern
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["carbon", "c"],
    }
    other_target_data = {
        "name": "carbon (3+)",  # Different name, but also has "carbon" in synonyms
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["carbon", "co2"],
    }

    source = Flow(source_data)
    target = Flow(target_data)
    other_target = Flow(other_target_data)

    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [other_target]
    )

    assert result is None, f"Expected result to be None when another target shares the same synonym, but got {result}"


def test_no_match_when_another_target_shares_same_synonym_reverse_case():
    """Test that no match occurs when another target flow shares the same synonym in reverse case (source has target name in synonyms)."""
    source_data = {
        "name": "nitrogen II",  # Ends with roman numeral
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["nitrogen", "n2"],
    }
    target_data = {
        "name": "nitrogen",
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["n2"],
    }
    other_target_data = {
        "name": "nitrogen III",  # Different name, but also has "nitrogen" in synonyms
        "context": ["air"],
        "unit": "kg",
        "synonyms": ["nitrogen", "n2"],
    }

    source = Flow(source_data)
    target = Flow(target_data)
    other_target = Flow(other_target_data)

    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [other_target]
    )

    assert result is None, f"Expected result to be None when another target shares the same synonym, but got {result}"


def test_match_when_another_target_shares_synonym_but_different_context():
    """Test that match occurs when another target flow shares the same synonym but has a different context."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",  # Ends with roman numeral
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }
    other_target_data = {
        "name": "water II",  # Different name, has "water" in synonyms, but different context
        "context": ["air"],  # Different context
        "unit": "kg",
        "synonyms": ["water", "h2o"],
    }

    source = Flow(source_data)
    target = Flow(target_data)
    other_target = Flow(other_target_data)

    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [other_target]
    )

    assert result == {"comment": "Identical preferred synonyms"}


def test_match_when_another_target_same_name_different_synonym():
    """Test that match occurs when another target flow has the same name but doesn't share the same synonym."""
    source_data = {
        "name": "water",
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o"],
    }
    target_data = {
        "name": "water I",  # Ends with roman numeral
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["water", "aqua"],
    }
    other_target_data = {
        "name": "water II",  # Different name, but doesn't have "water" in synonyms
        "context": ["ground"],
        "unit": "kg",
        "synonyms": ["h2o", "liquid"],  # "water" not in synonyms
    }

    source = Flow(source_data)
    target = Flow(target_data)
    other_target = Flow(other_target_data)

    result = match_identical_names_in_preferred_synonyms(
        source, target, [], [other_target]
    )

    assert result == {"comment": "Identical preferred synonyms"}
