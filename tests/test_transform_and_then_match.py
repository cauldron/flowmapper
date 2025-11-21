"""Tests for transform_and_then_match function."""

from copy import copy

import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.normalized_flow import NormalizedFlow
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
        transform_source_flows=[transform_func],
        transform_target_flows=[transform_func],
    )

    # Should match because both are transformed to "Modified name"
    assert len(matches) == 1, "Expected one match after transformation"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), f"Expected source flow to be reset after transformation, got {source_flows[0].current.name.data!r} != {source_normalized.name.data!r}"
    assert (
        target_flows[0].current.name.data == target_normalized.name.data
    ), f"Expected target flow to be reset after transformation, got {target_flows[0].current.name.data!r} != {target_normalized.name.data!r}"


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
        transform_source_flows=[transform_func],
        transform_target_flows=[transform_func],
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
            transform_source_flows=[transform_func],
            transform_target_flows=[transform_func],
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
        transform_source_flows=[transform_source],
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


def test_transform_and_then_match_with_list_of_transformations():
    """Test matching with a list of transformations applied in sequence."""
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

    def transform1(flows):
        for flow in flows:
            flow.update_current(name="First transformation")
        return flows

    def transform2(flows):
        for flow in flows:
            flow.update_current(name="Second transformation")
        return flows

    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=[transform1, transform2],
        transform_target_flows=[transform1, transform2],
    )

    # Should match because both are transformed through the same sequence
    assert len(matches) == 1, "Expected one match after multiple transformations"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset after transformations"
    assert (
        target_flows[0].current.name.data == target_normalized.name.data
    ), "Expected target flow to be reset after transformations"


def test_transform_and_then_match_list_transformations_sequence():
    """Test that list transformations are applied in the correct sequence."""
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

    # Track transformation order
    transform_order = []

    def transform1(flows):
        transform_order.append("transform1")
        for flow in flows:
            flow.update_current(name="Transform1")
        return flows

    def transform2(flows):
        transform_order.append("transform2")
        for flow in flows:
            flow.update_current(name="Transform2")
        return flows

    def transform3(flows):
        transform_order.append("transform3")
        for flow in flows:
            flow.update_current(name="Transform3")
        return flows

    # Apply transformations in sequence
    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=[transform1, transform2, transform3],
        transform_target_flows=[transform1, transform2, transform3],
    )

    # Verify transformations were applied in order
    assert transform_order == [
        "transform1",
        "transform2",
        "transform3",
        "transform1",
        "transform2",
        "transform3",
    ], f"Expected transformations in order, got {transform_order}"

    # Final name should be from transform3
    # But we need to check during matching, so let's verify the match happened
    assert len(matches) == 1, "Expected match after sequential transformations"


def test_transform_and_then_match_single_function_still_works():
    """Test that single function transformation works when wrapped in a list."""
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
            flow.update_current(name="Single transform")
        return flows

    # Test with single function wrapped in list
    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=[transform_func],
        transform_target_flows=[transform_func],
    )

    # Should match because both are transformed
    assert len(matches) == 1, "Expected one match with single transformation function"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset"


def test_transform_and_then_match_mixed_single_and_list():
    """Test matching with single function for source and list for target."""
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

    def single_transform(flows):
        for flow in flows:
            flow.update_current(name="Single")
        return flows

    def list_transform1(flows):
        for flow in flows:
            flow.update_current(name="List1")
        return flows

    def list_transform2(flows):
        for flow in flows:
            flow.update_current(name="List2")
        return flows

    # Source: single function in list, Target: list of functions
    matches = transform_and_then_match(
        source_flows=source_flows,
        target_flows=target_flows,
        match_function=match_identical_names,
        transform_source_flows=[single_transform],
        transform_target_flows=[list_transform1, list_transform2],
    )

    # Should not match because names differ: "Single" vs "List2"
    assert len(matches) == 0, "Expected no match when transformations differ"

    # Verify flows are reset
    assert (
        source_flows[0].current.name.data == source_normalized.name.data
    ), "Expected source flow to be reset"
