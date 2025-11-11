import json
from pathlib import Path

from flowmapper.domain import Flow
from flowmapper.flowmap import Flowmap
from flowmapper.transformation_mapping import prepare_transformations

DATA_DIR = Path(__file__).parent / "data"


def test_transform_flow_without_default_transformations():
    transformations = prepare_transformations(
        [json.load(open(DATA_DIR / "transformations.json"))]
    )
    source_flows = json.load(open(DATA_DIR / "sp.json"))
    source_flows = [Flow(flow, transformations) for flow in source_flows]
    target_flows = json.load(open(DATA_DIR / "ei-3.7.json"))
    target_flows = [Flow(flow, transformations) for flow in target_flows]

    flowmap = Flowmap(source_flows, target_flows)
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
                "cas_number": "cas_number",
            },
        },
        mapping_target={
            "expression language": "test",
            "labels": {
                "name": "name",
                "context": "context",
                "unit": "unit",
                "identifier": "identifier",
                "cas_number": "cas_number",
                "location": "location",
            },
        },
    )
    actual = dp.data["update"]

    expected = [
        {
            "source": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "context": "air",
                "cas_number": "110-63-4",
            },
            "target": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "context": ["air", "unspecified"],
                "cas_number": "110-63-4",
            },
            "conversion_factor": 1.0,
            "comment": "Identical names",
        },
        {
            "source": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "context": "air/high. pop.",
                "cas_number": "110-63-4",
            },
            "target": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "context": ["air", "unspecified"],
                "cas_number": "110-63-4",
            },
            "conversion_factor": 1.0,
            "comment": "Identical names",
        },
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_transform_flow_with_default_transformations(transformations):
    all_transformations = transformations + prepare_transformations(
        [json.load(open(DATA_DIR / "transformations.json"))]
    )
    source_flows = json.load(open(DATA_DIR / "sp.json"))
    source_flows = [Flow(flow, all_transformations) for flow in source_flows]
    target_flows = json.load(open(DATA_DIR / "ei-3.7.json"))
    target_flows = [Flow(flow, all_transformations) for flow in target_flows]

    flowmap = Flowmap(source_flows, target_flows)
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
                "cas_number": "cas_number",
            },
        },
        mapping_target={
            "expression language": "test",
            "labels": {
                "name": "name",
                "context": "context",
                "unit": "unit",
                "identifier": "identifier",
                "cas_number": "cas_number",
                "location": "location",
            },
        },
    )
    actual = dp.data["update"]

    expected = [
        {
            "comment": "Identical names",
            "conversion_factor": 1.0,
            "source": {
                "cas_number": "110-63-4",
                "context": "air",
                "name": "1,4-Butanediol",
                "unit": "kg",
            },
            "target": {
                "cas_number": "110-63-4",
                "context": ["air", "unspecified"],
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "name": "1,4-Butanediol",
                "unit": "kg",
            },
        },
        {
            "comment": "Identical names",
            "conversion_factor": 1.2142857142857142,
            "source": {
                "context": "air/low. pop.",
                "name": "Ammonia, as N",
                "unit": "kg",
            },
            "target": {
                "cas_number": "7664-41-7",
                "context": ["air", "non-urban air or from high stacks"],
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "name": "Ammonia",
                "unit": "kg",
            },
        },
        {
            "comment": "Name matching with location code",
            "conversion_factor": 1.0,
            "location": "FR",
            "source": {"context": "air/low. pop.", "name": "Ammonia, FR", "unit": "kg"},
            "target": {
                "cas_number": "7664-41-7",
                "context": ["air", "non-urban air or from high stacks"],
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "name": "Ammonia",
                "unit": "kg",
            },
        },
    ]

    assert actual == expected
