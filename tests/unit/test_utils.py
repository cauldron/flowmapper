"""Unit tests for utils module."""

from copy import copy

from flowmapper.domain import Flow, NormalizedFlow
from flowmapper.utils import FlowTransformationContext


class TestFlowTransformationContext:
    """Test FlowTransformationContext context manager."""

    def test_single_function_applied_and_reset(self):
        """Test that a single function is applied on entry and flows are reset on exit."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        def update_name(flows):
            for flow in flows:
                flow.update_current(name="Modified name")

        # Before context
        assert (
            flows[0].name == normalized.name
        ), "Expected current to match normalized before context"

        # Inside context
        with FlowTransformationContext(flows, update_name):
            assert (
                flows[0].name == "Modified name"
            ), f"Expected name to be 'Modified name' inside context, but got {flows[0].name!r}"

        # After context
        assert (
            flows[0].name == normalized.name
        ), f"Expected current to be reset to normalized after context, but got {flows[0].name!r} != {normalized.name!r}"

    def test_multiple_functions_applied_in_order(self):
        """Test that multiple functions are applied in order."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        call_order = []

        def update_name(flows):
            call_order.append("name")
            for flow in flows:
                # update_current always starts from normalized, so we need to update all fields together
                flow.update_current(name="Modified name", unit=flow.unit, context=flow.context)

        def update_unit(flows):
            call_order.append("unit")
            for flow in flows:
                # Preserve name from previous update, but update_current resets to normalized
                # So we need to get current values first
                current_name = flow.name
                current_context = flow.context
                flow.update_current(name=current_name, unit="g", context=current_context)

        def update_context(flows):
            call_order.append("context")
            for flow in flows:
                # Preserve previous updates
                current_name = flow.name
                current_unit = flow.unit
                flow.update_current(name=current_name, unit=current_unit, context="water")

        with FlowTransformationContext(flows, update_name, update_unit, update_context):
            assert (
                flows[0].name == "Modified name"
            ), "Expected name to be updated"
            assert flows[0].unit == "g", "Expected unit to be updated"
            assert (
                flows[0].context == "water"
            ), "Expected context to be updated"
            assert call_order == [
                "name",
                "unit",
                "context",
            ], f"Expected functions to be called in order, but got {call_order}"

        # After context, all should be reset
        assert (
            flows[0].name == normalized.name
        ), "Expected name to be reset"
        assert (
            flows[0].unit == normalized.unit
        ), "Expected unit to be reset"
        assert (
            flows[0].context == normalized.context
        ), "Expected context to be reset"

    def test_multiple_flows_all_reset(self):
        """Test that all flows in the list are reset on exit."""
        data1 = {"name": "Flow 1", "context": "air", "unit": "kg"}
        data2 = {"name": "Flow 2", "context": "water", "unit": "kg"}
        original1 = Flow.from_dict(data1)
        original2 = Flow.from_dict(data2)
        normalized1 = original1.normalize()
        normalized2 = original2.normalize()
        flows = [
            NormalizedFlow(
                original=original1, normalized=normalized1, current=copy(normalized1)
            ),
            NormalizedFlow(
                original=original2, normalized=normalized2, current=copy(normalized2)
            ),
        ]

        def update_all(flows):
            for flow in flows:
                flow.update_current(name="Updated")

        with FlowTransformationContext(flows, update_all):
            assert flows[0].name == "Updated", "Expected flow 0 to be updated"
            assert flows[1].name == "Updated", "Expected flow 1 to be updated"

        # After context, both should be reset
        assert (
            flows[0].name == normalized1.name
        ), f"Expected flow 0 to be reset, but got {flows[0].name!r}"
        assert (
            flows[1].name == normalized2.name
        ), f"Expected flow 1 to be reset, but got {flows[1].name!r}"

    def test_empty_flows_list(self):
        """Test that context manager works with empty flows list."""
        flows = []

        def noop(flows):
            pass

        # Should not raise any errors
        with FlowTransformationContext(flows, noop):
            pass

        assert flows == [], "Expected flows list to remain empty"

    def test_no_functions_provided(self):
        """Test that context manager works with no functions provided."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        # Should not raise any errors
        with FlowTransformationContext(flows):
            assert (
                flows[0].name == normalized.name
            ), "Expected flow to remain unchanged when no functions provided"

        # Should still be reset (though it's already in normalized state)
        assert (
            flows[0].name == normalized.name
        ), "Expected flow to remain in normalized state"

    def test_reset_on_exception(self):
        """Test that flows are reset even if an exception occurs."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        def update_name(flows):
            for flow in flows:
                flow.update_current(name="Modified name")

        try:
            with FlowTransformationContext(flows, update_name):
                assert (
                    flows[0].name == "Modified name"
                ), "Expected name to be modified"
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Flow should still be reset despite the exception
        assert (
            flows[0].name == normalized.name
        ), f"Expected flow to be reset after exception, but got {flows[0].name!r}"

    def test_context_manager_returns_self(self):
        """Test that context manager returns itself on entry."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        def noop(flows):
            pass

        with FlowTransformationContext(flows, noop) as ctx:
            assert (
                ctx is not None
            ), "Expected context manager to return itself"
            assert isinstance(
                ctx, FlowTransformationContext
            ), "Expected context manager to return FlowTransformationContext instance"

    def test_multiple_functions_with_different_updates(self):
        """Test multiple functions updating different fields."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "location": "US",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        def update_name(flows):
            for flow in flows:
                # update_current resets to normalized, so preserve other fields
                flow.update_current(
                    name="CO2",
                    unit=flow.unit,
                    context=flow.context,
                    location=flow.location,
                )

        def update_location(flows):
            for flow in flows:
                # Preserve name from previous update
                flow.update_current(
                    name=flow.name,
                    unit=flow.unit,
                    context=flow.context,
                    location="CA",
                )

        with FlowTransformationContext(flows, update_name, update_location):
            assert flows[0].name == "CO2", "Expected name to be updated"
            assert (
                flows[0].location == "CA"
            ), "Expected location to be updated"
            # Unit should remain as normalized (not updated by any function)
            assert (
                flows[0].unit == normalized.unit
            ), "Expected unit to remain unchanged"

        # All should be reset
        assert (
            flows[0].name == normalized.name
        ), "Expected name to be reset"
        assert (
            flows[0].location == normalized.location
        ), "Expected location to be reset"

    def test_function_modifies_multiple_flows_differently(self):
        """Test that a function can modify different flows differently."""
        data1 = {"name": "Flow 1", "context": "air", "unit": "kg"}
        data2 = {"name": "Flow 2", "context": "water", "unit": "kg"}
        original1 = Flow.from_dict(data1)
        original2 = Flow.from_dict(data2)
        normalized1 = original1.normalize()
        normalized2 = original2.normalize()
        flows = [
            NormalizedFlow(
                original=original1, normalized=normalized1, current=copy(normalized1)
            ),
            NormalizedFlow(
                original=original2, normalized=normalized2, current=copy(normalized2)
            ),
        ]

        def update_selectively(flows):
            # Only update the first flow
            flows[0].update_current(name="Updated Flow 1")

        with FlowTransformationContext(flows, update_selectively):
            assert (
                flows[0].name == "Updated Flow 1"
            ), "Expected flow 0 to be updated"
            assert (
                flows[1].name == normalized2.name
            ), "Expected flow 1 to remain unchanged"

        # Both should be reset
        assert (
            flows[0].name == normalized1.name
        ), "Expected flow 0 to be reset"
        assert (
            flows[1].name == normalized2.name
        ), "Expected flow 1 to be reset"

    def test_nested_context_managers(self):
        """Test nested context managers."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        original = Flow.from_dict(data)
        normalized = original.normalize()
        flows = [
            NormalizedFlow(
                original=original, normalized=normalized, current=copy(normalized)
            )
        ]

        def update_name(flows):
            for flow in flows:
                flow.update_current(name="Name Updated")

        def update_unit(flows):
            for flow in flows:
                # Preserve name from outer context
                flow.update_current(
                    name=flow.name,
                    unit="g",
                    context=flow.context,
                )

        with FlowTransformationContext(flows, update_name):
            assert flows[0].name == "Name Updated", "Expected name updated"
            assert (
                flows[0].unit == normalized.unit
            ), "Expected unit unchanged"

            with FlowTransformationContext(flows, update_unit):
                assert (
                    flows[0].name == "Name Updated"
                ), "Expected name still updated"
                assert flows[0].unit == "g", "Expected unit updated"

            # After inner context exits, it resets to normalized (original state)
            # This means the outer context's changes are lost
            assert (
                flows[0].name == normalized.name
            ), "Expected name reset to normalized after inner context exits"
            assert (
                flows[0].unit == normalized.unit
            ), "Expected unit reset to normalized after inner context exits"

        # After outer context, everything should still be reset (already reset by inner)
        assert (
            flows[0].name == normalized.name
        ), "Expected name reset after outer context"
        assert (
            flows[0].unit == normalized.unit
        ), "Expected unit reset after outer context"

