"""Tests for transform_and_then_match function."""

from copy import copy

import pytest

from flowmapper.domain import Flow, NormalizedFlow
from flowmapper.matching import match_identical_names, transform_and_then_match


def test_transform_and_then_match_basic():
    """Test basic matching without transformations or filters."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
    )

    assert len(matches) == 1, "Expected one match"
    assert matches[0].source == source_flow, "Expected match to reference source flow"
    assert matches[0].target == target_flow, "Expected match to reference target flow"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset"
    assert (
        target_flows[0].current.name.data == target_normalized.name.data
    ), "Expected target flow to be reset"


def test_transform_and_then_match_with_transformation():
    """Test matching with transformations applied."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    def transform_func(flows):
        for flow in flows:
            flow.update_current(name="Modified name")
        return flows

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=transform_func,
        transform_target_flows=transform_func,
    )

    # Should match because both are transformed to "Modified name"
    assert len(matches) == 1, "Expected one match after transformation"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data
        == source_normalized.name.data
        == "Carbon dioxide"
    ), "Expected source flow to be reset after transformation"
    assert (
        target_flows[0].current.name.data
        == target_normalized.name.data
        == "Carbon dioxide"
    ), "Expected target flow to be reset after transformation"


def test_transform_and_then_match_with_filter():
    """Test matching with filters applied."""
    source_data1 = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    source_data2 = {
        "name": "Water",
        "context": "water",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow1 = Flow.from_dict(source_data1)
    source_flow2 = Flow.from_dict(source_data2)
    target_flow = Flow.from_dict(target_data)

    source_flows = [
        NormalizedFlow(
            original=source_flow1,
            normalized=source_flow1.normalize(),
            current=copy(source_flow1.normalize()),
        ),
        NormalizedFlow(
            original=source_flow2,
            normalized=source_flow2.normalize(),
            current=copy(source_flow2.normalize()),
        ),
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_flow.normalize(),
            current=copy(target_flow.normalize()),
        )
    ]

    def filter_air_flows(flows):
        return [f for f in flows if "air" in str(f.current.context)]

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        filter_source_flows=filter_air_flows,
    )

    # Should match only the carbon dioxide flow (air context), not water
    assert len(matches) == 1, "Expected one match after filtering"
    assert (
        matches[0].source == source_flow1
    ), "Expected match to reference filtered source flow"

    # Verify all flows are reset (including the filtered one)
    assert (
        source_flows[0].current.name.data == source_flow1.normalize().name.data
    ), "Expected first source flow to be reset"
    assert (
        source_flows[1].current.name.data == source_flow2.normalize().name.data
    ), "Expected second source flow to be reset"


def test_transform_and_then_match_with_transform_and_filter():
    """Test matching with both transformations and filters."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    def transform_func(flows):
        for flow in flows:
            flow.update_current(name="Transformed name")
        return flows

    def filter_func(flows):
        # Filter to only flows with "Transformed" in name
        return [f for f in flows if "Transformed" in f.current.name.data]

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=transform_func,
        transform_target_flows=transform_func,
        filter_source_flows=filter_func,
        filter_target_flows=filter_func,
    )

    # Should match because both are transformed and pass filter
    assert len(matches) == 1, "Expected one match after transformation and filtering"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset"


def test_transform_and_then_match_resets_on_exception():
    """Test that flows are NOT reset when match function raises exception."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    def transform_func(flows):
        for flow in flows:
            flow.update_current(name="Modified")
        return flows

    def failing_match_function(source_flows, target_flows):
        raise ValueError("Test exception")

    try:
        transform_and_then_match(
            source_flows=source_flows,
            target_flows=target_flows,
            match_function=failing_match_function,
            transform_source_flows=transform_func,
            transform_target_flows=transform_func,
        )
    except ValueError:
        pass

    # Verify flows are NOT reset when exception occurs
    # (This documents current behavior - flows are only reset on success)
    assert (
        source_flows[0].current.name.data == "Modified"
    ), "Expected source flow to NOT be reset when exception occurs"
    assert (
        target_flows[0].current.name.data == "Modified"
    ), "Expected target flow to NOT be reset when exception occurs"


def test_transform_and_then_match_only_source_transformation():
    """Test matching with only source flow transformation."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    def transform_source(flows):
        for flow in flows:
            flow.update_current(name="Modified source")
        return flows

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=transform_source,
    )

    # Should not match because only source is transformed
    assert len(matches) == 0, "Expected no match when only source is transformed"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset"


def test_transform_and_then_match_filter_returns_empty_list():
    """Test matching when filter returns empty list."""
    source_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }
    target_data = {
        "name": "Carbon dioxide",
        "context": "air",
        "unit": "kg",
    }

    source_flow = Flow.from_dict(source_data)
    target_flow = Flow.from_dict(target_data)
    source_normalized = source_flow.normalize()
    target_normalized = target_flow.normalize()

    source_flows = [
        NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )
    ]
    target_flows = [
        NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )
    ]

    def filter_nothing(flows):
        return []

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        filter_source_flows=filter_nothing,
    )

    # Should have no matches because filter returns empty list
    assert len(matches) == 0, "Expected no matches when filter returns empty list"

    # Verify flows are still reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset even when filtered out"
