from flowmapper.flow import Flow
from flowmapper.match import match_identical_names_except_missing_suffix


def test_match_identical_names_except_missing_suffix(transformations):
    source = {
        "name": "Copper",
        "cas_number": "007440-50-8",
        "unit": "kg",
        "context": "Emissions to water/groundwater",
        "identifier": "F277F190-A8A4-4A2D-AAF6-F6CB3772A545",
    }
    target = {
        "name": "Copper, ion",
        "cas_number": "017493-86-6",
        "unit": "kg",
        "context": "water/ground-",
        "identifier": "c3b659e5-35f1-408c-8cb5-b5f9b295c76e",
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    result = match_identical_names_except_missing_suffix(s, t, [], [], suffix="ion")
    assert result, f"Expected match_identical_names_except_missing_suffix to return a truthy value, but got {result}"


def test_match_identical_names_except_missing_suffix_different_order(transformations):
    s = Flow(
        {"name": "Iron, ion", "unit": "g", "context": ["Emissions to air", ""]},
        transformations,
    )
    t = Flow(
        {
            "identifier": "8dba66e2-0f2e-4038-84ef-1e40b4f573a6",
            "cas_number": "007439-89-6",
            "name": "Iron",
            "unit": "kg",
            "context": ["air", "unspecified"],
        },
        transformations,
    )

    result = match_identical_names_except_missing_suffix(s, t, [], [], suffix="ion")
    assert result, f"Expected match_identical_names_except_missing_suffix to return a truthy value, but got {result}"
