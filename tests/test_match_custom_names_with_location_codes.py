from flowmapper.flow import Flow
from flowmapper.match import match_custom_names_with_location_codes


def test_match_custom_names_with_location_codes_extra():
    s = Flow(
        {
            "name": "Water (ersatz), net cons., irrigation, HU",
            "context": "air",
            "unit": "kg",
        }
    )
    t = Flow(
        {"name": "water, unspecified natural origin", "context": "air", "unit": "kg"}
    )

    actual = match_custom_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Custom names with location code",
        "location": "HU",
        "irrigation": True,
    }
    assert actual == expected


def test_match_custom_names_with_location_codes_no_extra():
    s = Flow({"name": "Water, well, HU", "context": "air", "unit": "kg"})
    t = Flow({"name": "Water, well, in ground", "context": "air", "unit": "kg"})

    actual = match_custom_names_with_location_codes(s, t, [], [])
    expected = {"comment": "Custom names with location code", "location": "HU"}
    assert actual == expected


def test_match_custom_names_with_location_codes_extra_whitespace_complicated():
    s = Flow(
        {
            "name": "Water (ersatz), net cons., irrigation,  \t RER w/o DE+NL+NO",
            "context": "air",
            "unit": "kg",
        }
    )
    t = Flow(
        {"name": "water, unspecified natural origin", "context": "air", "unit": "kg"}
    )

    actual = match_custom_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Custom names with location code",
        "location": "RER w/o DE+NL+NO",
        "irrigation": True,
    }
    assert actual == expected


def test_match_custom_names_with_location_codes_no_match():
    s = Flow({"name": "Ersatz water, RER w/o DE+NL+NO", "context": "air", "unit": "kg"})
    t = Flow(
        {"name": "water, unspecified natural origin", "context": "air", "unit": "kg"}
    )
    assert match_custom_names_with_location_codes(s, t, [], []) is None


def test_match_custom_names_with_location_codes_conversion():
    s = Flow({"name": "Water, well, HU", "context": "air", "unit": "kilogram"})
    t = Flow(
        {"name": "Water, well, in ground", "context": "air", "unit": "cubic_meter"}
    )

    actual = match_custom_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Custom names with location code",
        "location": "HU",
        "conversion_factor": 0.001,
    }
    assert actual == expected

    s = Flow({"name": "Water, well, HU", "context": "air", "unit": "cubic_meter"})
    t = Flow({"name": "Water, well, in ground", "context": "air", "unit": "kilogram"})

    actual = match_custom_names_with_location_codes(s, t, [], [])
    expected = {
        "comment": "Custom names with location code",
        "location": "HU",
        "conversion_factor": 1000.0,
    }
    assert actual == expected
