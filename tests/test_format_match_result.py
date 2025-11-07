from deepdiff import DeepDiff

from flowmapper.flow import Flow
from flowmapper.match import format_match_result


def test_format_match_result_missing_id(transformations):
    source = {
        "name": "Carbon dioxide, in air",
        "context": "Raw materials",
        "unit": "kg",
    }
    s = Flow(source, transformations)

    target = {
        "identifier": "cc6a1abb-b123-4ca6-8f16-38209df609be",
        "name": "Carbon dioxide, in air",
        "context": "natural resource/in air",
        "unit": "kg",
    }
    t = Flow(target)

    actual = format_match_result(s, t, 1.0, {"comment": "foo"})
    expected = {
        "source": {
            "name": "Carbon dioxide, in air",
            "context": "Raw materials",
            "unit": "kg",
        },
        "target": {
            "identifier": "cc6a1abb-b123-4ca6-8f16-38209df609be",
            "name": "Carbon dioxide, in air",
            "context": "natural resource/in air",
            "unit": "kg",
        },
        "conversion_factor": 1.0,
        "comment": "foo",
    }

    assert not DeepDiff(actual, expected)
