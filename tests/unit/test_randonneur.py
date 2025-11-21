"""Unit tests for randonneur-based transformation utilities."""

from flowmapper.domain.flow import Flow
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.utils import apply_transformation_and_convert_flows_to_normalized_flows


class TestApplyGenericTransformationsToFlows:
    """Test apply_transformation_and_convert_flows_to_normalized_flows function."""

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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
            functions=[], flows=[flow]
        )

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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
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

        result = apply_transformation_and_convert_flows_to_normalized_flows(
            functions=[transform_first, transform_second], flows=[flow]
        )

        assert call_order == [
            "first",
            "second",
        ], "Expected functions to be called in order"
        assert (
            "second" in result[0].normalized.name.data.lower()
        ), "Expected second transformation to be applied last"
