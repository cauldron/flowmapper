"""Unit tests for FlowTransformationContext."""

from copy import copy

import pytest

from flowmapper.domain import Flow, NormalizedFlow
from flowmapper.utils import FlowTransformationContext


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
