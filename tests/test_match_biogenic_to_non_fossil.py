from flowmapper.domain import Flow
from flowmapper.match import match_biogenic_to_non_fossil


def test_match_biogenic_to_non_fossil():
    s = Flow({"name": "Oils, biogenic", "context": "air", "unit": "kg"})
    t = Flow({"name": "Oils, non-fossil", "context": "air", "unit": "kg"})

    actual = match_biogenic_to_non_fossil(s, t, [], [])
    expected = {"comment": "Biogenic to non-fossil if no better match"}
    assert actual == expected, f"Expected actual to equal {expected}, but got {actual}"
