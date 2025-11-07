import math

from flowmapper.flow import Flow


def test_get_conversion_factor(transformations):
    s = Flow(
        {
            "name": "Protactinium-234",
            "unit": "Bq",
            "context": ["Emissions to air", "low. pop."],
        },
        transformations,
    )

    t = Flow(
        {
            "identifier": "fb13070e-06f1-4964-832f-a23945b880cc",
            "name": "Protactinium-234",
            "unit": "kBq",
            "context": ["air", "non-urban air or from high stacks"],
        },
        transformations,
    )

    actual = s.unit.conversion_factor(t.unit)
    expected = 1e-3
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_get_conversion_factor_water(transformations):
    s = Flow(
        {"name": "Water", "unit": "kg", "context": ["Emissions to water", ""]},
        transformations,
    )

    t = Flow(
        {
            "identifier": "2404b41a-2eed-4e9d-8ab6-783946fdf5d6",
            "CAS number": "007732-18-5",
            "name": "Water",
            "unit": "m3",
            "context": ["water", "unspecified"],
        },
        transformations,
    )

    actual = s.unit.conversion_factor(t.unit)
    assert math.isnan(actual), f"Expected actual to be NaN, but got {actual}"


def test_get_conversion_factor_m3y(transformations):
    s = Flow(
        {
            "name": "Volume occupied, reservoir",
            "unit": "m3y",
            "context": ["Resources", "in water"],
        },
        transformations,
    )

    t = Flow(
        {
            "identifier": "9a9d71c7-79f7-42d0-af47-282d22a7cf07",
            "name": "Volume occupied, reservoir",
            "unit": "m3*year",
            "context": ["natural resource", "in water"],
        },
        transformations,
    )

    actual = s.unit.conversion_factor(t.unit)
    expected = 1
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_get_conversion_factor_m2a(transformations):
    s = Flow(
        {
            "name": "Occupation, annual crop",
            "unit": "m2a",
            "context": ["Resources", "land"],
        },
        transformations,
    )

    t = Flow(
        {
            "identifier": "c5aafa60-495c-461c-a1d4-b262a34c45b9",
            "name": "Occupation, annual crop",
            "unit": "m2*year",
            "context": ["natural resource", "land"],
        },
        transformations,
    )

    actual = s.unit.conversion_factor(t.unit)
    expected = 1
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"


def test_get_conversion_factor_nan(transformations):
    s = Flow(
        {
            "name": "Radium-226/kg",
            "unit": "kg",
            "context": ["Emissions to water", ""],
        },
        transformations,
    )

    t = Flow(
        {
            "identifier": "74a0aabb-e11b-4f3b-8921-45e447b33393",
            "CAS number": "013982-63-3",
            "name": "Radium-226",
            "unit": "kBq",
            "context": ["water", "ocean"],
        },
        transformations,
    )

    actual = s.unit.conversion_factor(t.unit)
    assert math.isnan(actual), f"Expected actual to be NaN, but got {actual}"
