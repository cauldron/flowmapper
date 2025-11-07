from deepdiff import DeepDiff

from flowmapper.flow import Flow
from flowmapper.match import match_identical_names


def test_match_identical_names(transformations):
    source = {
        "name": "Carbon dioxide, in air",
        "CAS No": "000124-38-9",
        "unit": "kg",
        "context": "Resources/in air",
        "Flow UUID": "32722990-B7D8-44A8-BC7D-EC3A89F533FF",
    }

    target = {
        "name": "Carbon dioxide, in air",
        "CAS number": "000124-38-9",
        "unit": "kg",
        "context": "natural resource/in air",
        "identifier": "cc6a1abb-b123-4ca6-8f16-38209df609be",
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    match = match_identical_names(s, t, [], [])
    assert match


def test_match_identical_names_jsonpath(transformations):
    source = {
        "name": "Carbon dioxide, in air",
        "context": ["Raw", "(unspecified)"],
        "unit": "kg",
        "CAS": "000124-38-9",
    }

    target = {
        "identifier": "cc6a1abb-b123-4ca6-8f16-38209df609be",
        "CAS number": "000124-38-9",
        "name": "Carbon dioxide, in air",
        "unit": "kg",
        "context": ["natural resource", "in air"],
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    match = match_identical_names(s, t, [], [])
    assert not match
