from flowmapper.domain import Flow
from flowmapper.match import match_names_with_location_codes


def test_match_names_with_country_codes():
    s = Flow({"name": "Ammonia, NL", "context": "air", "unit": "kg"})
    t = Flow({"name": "Ammonia", "context": "air", "unit": "kg"})

    actual = match_names_with_location_codes(s, t, [], [])
    expected = {"comment": "Name matching with location code", "location": "NL"}
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_match_names_with_country_codes_extra_whitespace():
    s = Flow({"name": "Ammonia,  \tNL", "context": "air", "unit": "kg"})
    t = Flow({"name": "Ammonia", "context": "air", "unit": "kg"})

    actual = match_names_with_location_codes(s, t, [], [])
    expected = {"comment": "Name matching with location code", "location": "NL"}
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_match_names_with_country_codes_no_match():
    s = Flow({"name": "Ammonia-NL", "context": "air", "unit": "kg"})
    t = Flow({"name": "Ammonia", "context": "air", "unit": "kg"})
    result = match_names_with_location_codes(s, t, [], [])
    assert (
        result is None
    ), f"Expected match_names_with_location_codes to return None, but got {result}"


def test_match_names_with_country_codes_complicated_location():
    s = Flow({"name": "Ammonia, RER w/o DE+NL+NO", "context": "air", "unit": "kg"})
    t = Flow({"name": "Ammonia", "context": "air", "unit": "kg"})

    actual = match_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Name matching with location code",
        "location": "RER w/o DE+NL+NO",
    }
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_match_names_with_country_codes_water_source_conversion():
    s = Flow({"name": "Water, NL", "context": "air", "unit": "kilogram"})
    t = Flow({"name": "Water", "context": "air", "unit": "cubic_meter"})

    actual = match_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Name matching with location code",
        "location": "NL",
        "conversion_factor": 0.001,
    }
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_match_names_with_country_codes_water_target_conversion():
    s = Flow({"name": "Water, NL", "context": "air", "unit": "cubic_meter"})
    t = Flow({"name": "Water", "context": "air", "unit": "kilogram"})

    actual = match_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Name matching with location code",
        "location": "NL",
        "conversion_factor": 1000.0,
    }
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"
