from flowmapper.domain import Flow
from flowmapper.flowmap import Flowmap


def test_match_non_ionic_state():
    s = [
        Flow({"name": "Mercury (II)", "context": "air", "unit": "kg"}),
        Flow({"name": "Manganese (II)", "context": "air", "unit": "kg"}),
    ]
    t = [
        Flow({"name": "Mercury", "context": "air", "unit": "kg", "identifier": "foo"}),
        Flow(
            {
                "name": "Manganese II",
                "context": "air",
                "unit": "kg",
                "identifier": "bar",
            }
        ),
    ]

    flowmap = Flowmap(s, t)
    dp = flowmap.to_randonneur(
        source_id="test-source",
        target_id="test-target",
        contributors=[{"title": "Test", "roles": ["author"], "path": "test"}],
        mapping_source={
            "expression language": "test",
            "labels": {
                "name": "name",
                "context": "context",
                "unit": "unit",
            },
        },
        mapping_target={
            "expression language": "test",
            "labels": {
                "name": "name",
                "context": "context",
                "unit": "unit",
                "identifier": "identifier",
            },
        },
    )
    actual = dp.data["update"]
    expected = [
        {
            "source": {"name": "Manganese (II)", "context": "air", "unit": "kg"},
            "target": {
                "identifier": "bar",
                "name": "Manganese II",
                "context": "air",
                "unit": "kg",
            },
            "conversion_factor": 1.0,
            "comment": "With/without roman numerals in parentheses",
        },
        {
            "source": {"name": "Mercury (II)", "context": "air", "unit": "kg"},
            "target": {
                "identifier": "foo",
                "name": "Mercury",
                "context": "air",
                "unit": "kg",
            },
            "conversion_factor": 1.0,
            "comment": "Non-ionic state if no better match",
        },
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"
