"""Unit tests for randonneur-based transformation utilities."""

from copy import copy

import pytest

from flowmapper.domain import Flow, NormalizedFlow
from flowmapper.utils import (
    FlowTransformationContext,
    apply_generic_transformations_to_flows,
)


class TestFlowTransformationContext:
    """Test FlowTransformationContext context manager."""

    def test_single_function_applies_transformation(self):
        """Test that a single function is applied on entry."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )
        flows = [nf]

        def transform_func(flows):
            for flow in flows:
                flow.update_current(name="Modified name")
            return flows

        with FlowTransformationContext(flows, transform_func) as modified_flows:
            assert (
                modified_flows[0].current.name.data == "Modified name"
            ), "Expected flow to be modified in context"
            assert (
                flows[0].current.name.data == "Modified name"
            ), "Expected original flows list to be modified"

        # After exit, flows should be reset
        assert (
            flows[0].current.name.data == normalized.name.data
        ), "Expected flow to be reset after context exit"

    def test_enter_returns_modified_flows(self):
        """Test that __enter__ returns the modified flows list."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )
        flows = [nf]

        def transform_func(flows):
            for flow in flows:
                flow.update_current(name="Modified")
            return flows

        context = FlowTransformationContext(flows, transform_func)
        returned_flows = context.__enter__()

        assert (
            returned_flows is flows
        ), "Expected __enter__ to return the same flows list object"
        assert (
            returned_flows[0].current.name.data == "Modified"
        ), "Expected returned flows to be modified"

        context.__exit__(None, None, None)

    def test_reset_on_exit(self):
        """Test that flows are reset to normalized state on exit."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )
        flows = [nf]

        def transform_func(flows):
            for flow in flows:
                flow.update_current(name="Modified", unit="g", context="water")
            return flows

        with FlowTransformationContext(flows, transform_func):
            # Verify modifications
            assert flows[0].current.name.data == "Modified"
            assert flows[0].current.unit.data == "g"
            assert flows[0].current.context.value == "water"

        # After exit, all should be reset
        assert (
            flows[0].current.name.data == normalized.name.data
        ), "Expected name to be reset"
        assert (
            flows[0].current.unit.data == normalized.unit.data
        ), "Expected unit to be reset"
        assert (
            flows[0].current.context.value == normalized.context.value
        ), "Expected context to be reset"

    def test_reset_on_exception(self):
        """Test that flows are reset even when an exception occurs."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )
        flows = [nf]

        def transform_func(flows):
            for flow in flows:
                flow.update_current(name="Modified")
            return flows

        try:
            with FlowTransformationContext(flows, transform_func):
                assert flows[0].current.name.data == "Modified"
                raise ValueError("Test exception")
        except ValueError:
            pass

        # After exception, flows should still be reset
        assert (
            flows[0].current.name.data == normalized.name.data
        ), "Expected flow to be reset even after exception"

    def test_function_returns_modified_list(self):
        """Test that functions can return a modified list."""
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        data2 = {
            "name": "Water",
            "context": "air",
            "unit": "kg",
        }
        original1 = Flow.from_dict(data1)
        original2 = Flow.from_dict(data2)
        normalized1 = original1.normalize()
        normalized2 = original2.normalize()
        nf1 = NormalizedFlow(
            original=original1, normalized=normalized1, current=copy(normalized1)
        )
        nf2 = NormalizedFlow(
            original=original2, normalized=normalized2, current=copy(normalized2)
        )
        flows = [nf1, nf2]

        def filter_func(flows):
            # Return only flows with "carbon" in name
            filtered = [f for f in flows if "carbon" in f.current.name.data.lower()]
            for flow in filtered:
                flow.update_current(name="Filtered")
            return filtered

        with FlowTransformationContext(flows, filter_func) as modified_flows:
            assert (
                len(modified_flows) == 1
            ), "Expected filtered list to have one element"
            assert (
                modified_flows[0].current.name.data == "Filtered"
            ), "Expected filtered flow to be modified"

        # Original flows list should still have both flows
        assert len(flows) == 2, "Expected original flows list to be unchanged"

    def test_multiple_flows_all_reset(self):
        """Test that all flows in the list are reset."""
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        data2 = {
            "name": "Water",
            "context": "air",
            "unit": "kg",
        }
        original1 = Flow.from_dict(data1)
        original2 = Flow.from_dict(data2)
        normalized1 = original1.normalize()
        normalized2 = original2.normalize()
        nf1 = NormalizedFlow(
            original=original1, normalized=normalized1, current=copy(normalized1)
        )
        nf2 = NormalizedFlow(
            original=original2, normalized=normalized2, current=copy(normalized2)
        )
        flows = [nf1, nf2]

        def transform_func(flows):
            for i, flow in enumerate(flows):
                flow.update_current(name=f"Modified {i}")
            return flows

        with FlowTransformationContext(flows, transform_func):
            assert flows[0].current.name.data == "Modified 0"
            assert flows[1].current.name.data == "Modified 1"

        # Both should be reset
        assert (
            flows[0].current.name.data == normalized1.name.data
        ), "Expected first flow to be reset"
        assert (
            flows[1].current.name.data == normalized2.name.data
        ), "Expected second flow to be reset"

    def test_no_functions(self):
        """Test that context manager works with no functions."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )
        flows = [nf]

        with FlowTransformationContext(flows) as returned_flows:
            assert returned_flows is flows, "Expected same flows list to be returned"
            assert (
                returned_flows[0].current.name.data == normalized.name.data
            ), "Expected flows to be unchanged"

        # Should still reset (though nothing changed)
        assert (
            flows[0].current.name.data == normalized.name.data
        ), "Expected flow to remain normalized"


class TestApplyGenericTransformationsToFlows:
    """Test apply_generic_transformations_to_flows function."""

    def test_basic_transformation_single_function(self):
        """Test basic transformation with a single function."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        def transform_func(graph):
            # Modify the name in the dict
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = "Modified name"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_func], flows=[flow]
        )

        assert len(result) == 1, "Expected one NormalizedFlow"
        assert isinstance(result[0], NormalizedFlow), "Expected NormalizedFlow object"
        assert result[0].original == flow, "Expected original flow to be preserved"
        assert (
            result[0].normalized.name.data == "modified name"
        ), "Expected normalized name to be transformed and normalized"
        assert (
            result[0].current.name.data == "modified name"
        ), "Expected current to match normalized"

    def test_multiple_transformations_sequential(self):
        """Test that multiple transformations are applied sequentially."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        def transform_name(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = "First transformation"
                result.append(modified)
            return result

        def transform_unit(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["unit"] = "g"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_name, transform_unit], flows=[flow]
        )

        assert len(result) == 1, "Expected one NormalizedFlow"
        # Both transformations should be applied
        assert (
            result[0].normalized.name.data == "first transformation"
        ), "Expected name to be transformed by first function"
        assert (
            result[0].original.unit.data == "kg"
        ), "Expected original unit to be preserved as `kg`"
        assert (
            result[0].normalized.unit.data == "gram"
        ), "Expected unit to be transformed by second function and normalized from `g` to `gram`"

    def test_empty_functions_list(self):
        """Test with empty list of functions (no transformations)."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        result = apply_generic_transformations_to_flows(functions=[], flows=[flow])

        assert len(result) == 1, "Expected one NormalizedFlow"
        assert result[0].original == flow, "Expected original flow to be preserved"
        # Without transformations, normalized should be the same as flow.normalize()
        expected_normalized = flow.normalize()
        assert (
            result[0].normalized.name.data == expected_normalized.name.data
        ), "Expected normalized to match flow.normalize()"

    def test_empty_flows_list(self):
        """Test with empty list of flows."""

        def transform_func(graph):
            return graph

        result = apply_generic_transformations_to_flows(
            functions=[transform_func], flows=[]
        )

        assert len(result) == 0, "Expected empty list"

    def test_multiple_flows(self):
        """Test transformation of multiple flows."""
        flow1 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        flow2 = Flow.from_dict({"name": "Water", "context": "water", "unit": "kg"})

        def transform_func(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = f"Modified {flow_dict['name']}"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_func], flows=[flow1, flow2]
        )

        assert len(result) == 2, "Expected two NormalizedFlow objects"
        assert (
            result[0].original == flow1
        ), "Expected first original flow to be preserved"
        assert (
            result[1].original == flow2
        ), "Expected second original flow to be preserved"
        assert (
            "modified carbon dioxide" in result[0].normalized.name.data.lower()
        ), "Expected first flow name to be transformed"
        assert (
            "modified water" in result[1].normalized.name.data.lower()
        ), "Expected second flow name to be transformed"

    def test_transformation_modifies_context(self):
        """Test transformation that modifies context."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        def transform_context(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["context"] = ("emissions", "to air")
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_context], flows=[flow]
        )

        assert len(result) == 1, "Expected one NormalizedFlow"
        # Context should be transformed and normalized
        assert isinstance(
            result[0].normalized.context.value, tuple
        ), "Expected context to be tuple"
        assert (
            "emissions" in result[0].normalized.context.value
        ), "Expected transformed context to be present"

    def test_transformation_modifies_multiple_fields(self):
        """Test transformation that modifies multiple fields at once."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "location": "US",
            }
        )

        def transform_multiple(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = "CO2"
                modified["unit"] = "g"
                modified["location"] = "CA"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_multiple], flows=[flow]
        )

        assert len(result) == 1, "Expected one NormalizedFlow"
        assert (
            result[0].normalized.name.data == "co2"
        ), "Expected name to be transformed"
        assert (
            result[0].normalized.unit.data == "gram"
        ), "Expected unit to be transformed to `g` and normalized to `gram`"
        assert (
            result[0].normalized.location == "CA"
        ), "Expected location to be transformed"

    def test_original_flows_unchanged(self):
        """Test that original Flow objects are not modified."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        original_name = flow.name.data

        def transform_func(graph):
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = "Modified name"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_func], flows=[flow]
        )

        # Original flow should be unchanged
        assert flow.name.data == original_name, "Expected original flow to be unchanged"
        assert result[0].original == flow, "Expected original reference to be preserved"

    def test_current_is_copy_of_normalized(self):
        """Test that current is a copy of normalized, not a reference."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        def transform_func(graph):
            return graph  # No transformation

        result = apply_generic_transformations_to_flows(
            functions=[transform_func], flows=[flow]
        )

        assert (
            result[0].current is not result[0].normalized
        ), "Expected current to be a copy, not a reference"
        assert (
            result[0].current.name.data == result[0].normalized.name.data
        ), "Expected current to have same data as normalized"

    def test_transformation_chain_preserves_order(self):
        """Test that transformations are applied in the correct order."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        call_order = []

        def transform_first(graph):
            call_order.append("first")
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = "First"
                result.append(modified)
            return result

        def transform_second(graph):
            call_order.append("second")
            result = []
            for flow_dict in graph:
                modified = flow_dict.copy()
                modified["name"] = f"{flow_dict['name']} then Second"
                result.append(modified)
            return result

        result = apply_generic_transformations_to_flows(
            functions=[transform_first, transform_second], flows=[flow]
        )

        assert call_order == [
            "first",
            "second",
        ], "Expected functions to be called in order"
        assert (
            "second" in result[0].normalized.name.data.lower()
        ), "Expected second transformation to be applied last"
