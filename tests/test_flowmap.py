import json
from pathlib import Path

import pandas as pd
import pytest

from flowmapper import Flowmap
from flowmapper.domain import Flow
from flowmapper.matching import match_emissions_with_suffix_ion, match_identical_names

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def source_flows(transformations):
    return [
        Flow(flow, transformations) for flow in json.load(open(DATA_DIR / "sp.json"))
    ]


@pytest.fixture
def target_flows(transformations):
    return [
        Flow(flow, transformations)
        for flow in json.load(open(DATA_DIR / "ei-3.7.json"))
    ]


@pytest.fixture
def ei39():
    return [Flow(flow) for flow in json.load(open(DATA_DIR / "ei-3.9.json"))]


@pytest.fixture
def ei310():
    return [Flow(flow) for flow in json.load(open(DATA_DIR / "ei-3.10.json"))]


def test_flowmap_remove_duplicates(source_flows, target_flows):
    flowmap = Flowmap(source_flows, target_flows)
    actual = flowmap.source_flows
    # Added one duplicate on purpose
    assert (
        len(flowmap.source_flows) == 7
    ), f"Expected len(flowmap.source_flows) to be 7, but got {len(flowmap.source_flows)}"


def test_flowmap_mappings(source_flows, target_flows):
    flowmap = Flowmap(source_flows, target_flows)
    actual = flowmap.mappings[0]
    expected_keys = [
        "from",
        "to",
        "conversion_factor",
        "match_rule",
        "match_rule_priority",
        "info",
    ]
    assert (
        list(actual.keys()) == expected_keys
    ), f"Expected actual.keys() to be {expected_keys}, but got {list(actual.keys())}"
    assert (
        actual["match_rule"] == "match_identical_names"
    ), f"Expected actual['match_rule'] to be 'match_identical_names', but got {actual['match_rule']!r}"


def test_flowmap_to_randonneur(source_flows, target_flows):
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
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_flowmap_to_randonneur_export(source_flows, target_flows, tmp_path):
    flowmap = Flowmap(source_flows, target_flows)
    flowmap.to_randonneur(
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
        path=tmp_path / "randonneur.json",
    )
    with open(tmp_path / "randonneur.json") as fs:
        data = json.load(fs)
        actual = data["update"]
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
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_flowmap_with_custom_rules_no_match(source_flows, target_flows):
    flowmap = Flowmap(
        source_flows,
        target_flows,
        rules=[match_emissions_with_suffix_ion],
    )
    actual = flowmap.mappings
    assert actual == [], f"Expected actual to be an empty list, but got {actual}"


def test_flowmap_with_custom_rules_match(source_flows, target_flows):
    flowmap = Flowmap(source_flows, target_flows, rules=[match_identical_names])
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
                "context": [
                    "air",
                    "unspecified",
                ],
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "name": "1,4-Butanediol",
                "unit": "kg",
            },
        }
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_flowmap_to_glad(source_flows, target_flows):
    flowmap = Flowmap(source_flows, target_flows)
    actual = flowmap.to_glad()
    expected = {
        "SourceFlowName": ["1,4-Butanediol", "Ammonia, FR"],
        "SourceFlowUUID": ["", ""],
        "SourceFlowContext": ["air", "air/low. pop."],
        "SourceUnit": ["kg", "kg"],
        "MatchCondition": ["=", "="],
        "ConversionFactor": [1.0, 1.0],
        "TargetFlowName": ["1,4-Butanediol", "Ammonia"],
        "TargetFlowUUID": [
            "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
            "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
        ],
        "TargetFlowContext": [
            "air✂️unspecified",
            "air✂️non-urban air or from high stacks",
        ],
        "TargetUnit": ["kg", "kg"],
        "MemoMapper": ["Identical names", "Name matching with location code"],
    }
    pd.testing.assert_frame_equal(actual, pd.DataFrame(expected))


def test_flowmap_to_glad_export(source_flows, target_flows, tmp_path):
    flowmap = Flowmap(source_flows, target_flows)
    flowmap.to_glad(tmp_path / "glad.xlsx")
    actual = pd.read_excel(tmp_path / "glad.xlsx")
    print(actual["MatchCondition"])
    expected = {
        "SourceFlowName": ["1,4-Butanediol", "Ammonia, FR"],
        "SourceFlowUUID": [float("NaN"), float("NaN")],
        "SourceFlowContext": ["air", "air/low. pop."],
        "SourceUnit": ["kg", "kg"],
        "MatchCondition": ["=", "="],
        "ConversionFactor": [1, 1],
        "TargetFlowName": ["1,4-Butanediol", "Ammonia"],
        "TargetFlowUUID": [
            "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
            "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
        ],
        "TargetFlowContext": [
            "air✂️unspecified",
            "air✂️non-urban air or from high stacks",
        ],
        "TargetUnit": ["kg", "kg"],
        "MemoMapper": ["Identical names", "Name matching with location code"],
    }
    pd.testing.assert_frame_equal(actual, pd.DataFrame(expected))


def test_flowmap_nomatch_rule(source_flows, target_flows):
    nomatch = lambda flow: flow.context == "air/urban air close to ground"
    flowmap = Flowmap(source_flows, target_flows, nomatch_rules=[nomatch])

    assert (
        len(flowmap.source_flows_nomatch) == 1
    ), f"Expected len(flowmap.source_flows_nomatch) to be 1, but got {len(flowmap.source_flows_nomatch)}"
    assert (
        flowmap.source_flows_nomatch[0].name == "1,4-Butanediol"
    ), f"Expected flowmap.source_flows_nomatch[0].name to be '1,4-Butanediol', but got {flowmap.source_flows_nomatch[0].name!r}"
    assert (
        flowmap.source_flows_nomatch[0].context == "air/urban air close to ground"
    ), f"Expected flowmap.source_flows_nomatch[0].context to be 'air/urban air close to ground', but got {flowmap.source_flows_nomatch[0].context!r}"
    assert (
        flowmap.source_flows[0].name == "1,4-Butanediol"
    ), f"Expected flowmap.source_flows[0].name to be '1,4-Butanediol', but got {flowmap.source_flows[0].name!r}"
    assert (
        flowmap.source_flows[0].context == "air"
    ), f"Expected flowmap.source_flows[0].context to be 'air', but got {flowmap.source_flows[0].context!r}"


def test_flowmap_nomatch_rule_false(source_flows, target_flows):
    nomatch = lambda flow: flow.context == "water"
    flowmap = Flowmap(source_flows, target_flows, nomatch_rules=[nomatch])
    assert (
        not flowmap.source_flows_nomatch
    ), f"Expected flowmap.source_flows_nomatch to be falsy, but got {flowmap.source_flows_nomatch}"


def test_flowmap_nomatch_multiple_rules(source_flows, target_flows):
    nomatch1 = lambda flow: flow.context == "air/urban air close to ground"
    nomatch2 = lambda flow: flow.context == "air"
    flowmap = Flowmap(source_flows, target_flows, nomatch_rules=[nomatch1, nomatch2])

    assert (
        len(flowmap.source_flows_nomatch) == 2
    ), f"Expected len(flowmap.source_flows_nomatch) to be 2, but got {len(flowmap.source_flows_nomatch)}"
    assert (
        flowmap.source_flows_nomatch[0].name == "1,4-Butanediol"
    ), f"Expected flowmap.source_flows_nomatch[0].name to be '1,4-Butanediol', but got {flowmap.source_flows_nomatch[0].name!r}"
    assert (
        flowmap.source_flows_nomatch[1].name == "1,4-Butanediol"
    ), f"Expected flowmap.source_flows_nomatch[1].name to be '1,4-Butanediol', but got {flowmap.source_flows_nomatch[1].name!r}"
    assert (
        flowmap.source_flows[0].name == "Cesium-134"
    ), f"Expected flowmap.source_flows[0].name to be 'Cesium-134', but got {flowmap.source_flows[0].name!r}"


def test_flowmap_mappings_ei_ei(target_flows):
    flowmap = Flowmap(target_flows, target_flows)
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
                "identifier": "identifier",
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
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "context": ["air", "unspecified"],
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
            "comment": "Identical identifier",
        },
        {
            "source": {
                "name": "Ammonia",
                "unit": "kg",
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "context": ["air", "non-urban air or from high stacks"],
                "cas_number": "7664-41-7",
            },
            "target": {
                "name": "Ammonia",
                "unit": "kg",
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "context": ["air", "non-urban air or from high stacks"],
                "cas_number": "7664-41-7",
            },
            "conversion_factor": 1.0,
            "comment": "Identical identifier",
        },
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_flowmap_mappings_ei39_ei310(ei39, ei310):
    flowmap = Flowmap(ei39, ei310)
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
                "identifier": "identifier",
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
                "name": "2,4-D amines",
                "unit": "kg",
                "identifier": "4f777e05-70f9-4a18-a406-d8232325073f",
                "context": ["air", "non-urban air or from high stacks"],
                "cas_number": "2008-39-1",
            },
            "target": {
                "name": "2,4-D dimethylamine salt",
                "unit": "kg",
                "identifier": "b6b4201e-0561-5992-912f-e729fbf04e41",
                "context": ["air", "non-urban air or from high stacks"],
                "cas_number": "2008-39-1",
            },
            "conversion_factor": 1.0,
            "comment": "Identical CAS numbers",
        }
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"
