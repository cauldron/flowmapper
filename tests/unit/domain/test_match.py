"""Unit tests for Match class."""

from copy import copy

import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.match import Match
from flowmapper.domain.match_condition import MatchCondition


class TestMatchInitialization:
    """Test Match class initialization."""

    def test_match_initialization_with_required_fields(self):
        """Test Match initialization with only required fields."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        assert match.source == source_flow, "Expected source to match"
        assert match.target == target_flow, "Expected target to match"
        assert match.function_name == "test_function", "Expected function_name to match"
        assert match.condition == MatchCondition.exact, "Expected condition to match"
        assert match.conversion_factor == 1.0, "Expected default conversion_factor"
        assert match.comment == "", "Expected default empty comment"
        assert (
            match.new_target_flow is False
        ), "Expected default new_target_flow to be False"

    def test_match_initialization_with_all_fields(self):
        """Test Match initialization with all fields including new_target_flow."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.related,
            conversion_factor=2.5,
            comment="Test comment",
            new_target_flow=True,
        )

        assert match.source == source_flow, "Expected source to match"
        assert match.target == target_flow, "Expected target to match"
        assert match.function_name == "test_function", "Expected function_name to match"
        assert match.condition == MatchCondition.related, "Expected condition to match"
        assert match.conversion_factor == 2.5, "Expected conversion_factor to match"
        assert match.comment == "Test comment", "Expected comment to match"
        assert match.new_target_flow is True, "Expected new_target_flow to be True"

    def test_match_initialization_with_new_target_flow_false(self):
        """Test Match initialization with new_target_flow explicitly set to False."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
            new_target_flow=False,
        )

        assert match.new_target_flow is False, "Expected new_target_flow to be False"

    def test_match_initialization_with_different_conditions(self):
        """Test Match initialization with different MatchCondition values."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        for condition in MatchCondition:
            match = Match(
                source=source_flow,
                target=target_flow,
                function_name="test_function",
                condition=condition,
                new_target_flow=True,
            )
            assert match.condition == condition, f"Expected condition to be {condition}"
            assert match.new_target_flow is True, "Expected new_target_flow to be True"


class TestMatchExport:
    """Test Match export method."""

    def test_export_basic(self):
        """Test basic export without metadata."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
            new_target_flow=True,
        )

        exported = match.export()

        assert "source" in exported, "Expected source in exported data"
        assert "target" in exported, "Expected target in exported data"
        # Export uses the original flow data (not normalized)
        assert (
            exported["source"]["name"] == "Carbon dioxide"
        ), "Expected source name in export"
        assert (
            exported["target"]["name"] == "Carbon dioxide"
        ), "Expected target name in export"
        # Condition is exported as SKOS URI via as_glad() method
        assert (
            exported["condition"] == "http://www.w3.org/2004/02/skos/core#exactMatch"
        ), "Expected condition as SKOS URI"
        assert exported["conversion_factor"] == 1.0, "Expected conversion_factor"
        assert exported["comment"] == "", "Expected comment"
        assert exported["new_target_flow"] is True, "Expected new_target_flow in export"
        assert "function_name" not in exported, "Expected function_name to be removed"

    def test_export_with_metadata(self):
        """Test export with flowmapper_metadata enabled."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.close,
            new_target_flow=False,
        )

        exported = match.export(flowmapper_metadata=True)

        assert (
            "flowmapper_metadata" in exported
        ), "Expected flowmapper_metadata in export"
        assert exported["flowmapper_metadata"]["function_name"] == "test_function"
        assert "version" in exported["flowmapper_metadata"]
        assert (
            exported["new_target_flow"] is False
        ), "Expected new_target_flow in export"

    def test_export_with_new_target_flow(self):
        """Test export includes new_target_flow attribute."""
        source_flow = Flow.from_dict(
            {"name": "Water", "context": "water", "unit": "kg"}
        )
        target_flow = Flow.from_dict(
            {"name": "Water", "context": "water", "unit": "kg"}
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.related,
            new_target_flow=True,
            comment="New target flow",
        )

        exported = match.export()

        assert (
            exported["new_target_flow"] is True
        ), "Expected new_target_flow to be True in export"
        assert (
            exported["comment"] == "New target flow"
        ), "Expected comment to be preserved"


class TestMatchComparison:
    """Test Match comparison methods."""

    def test_match_less_than_comparison(self):
        """Test Match __lt__ method for sorting."""
        source1 = Flow.from_dict({"name": "A", "context": "air", "unit": "kg"})
        target1 = Flow.from_dict({"name": "B", "context": "air", "unit": "kg"})
        source2 = Flow.from_dict({"name": "C", "context": "air", "unit": "kg"})
        target2 = Flow.from_dict({"name": "D", "context": "air", "unit": "kg"})

        match1 = Match(
            source=source1,
            target=target1,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=True,
        )
        match2 = Match(
            source=source2,
            target=target2,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=False,
        )

        assert match1 < match2, "Expected match1 to be less than match2"
        assert not (match2 < match1), "Expected match2 not to be less than match1"

    def test_match_comparison_with_same_source_different_target(self):
        """Test Match comparison with same source but different target."""
        source = Flow.from_dict({"name": "A", "context": "air", "unit": "kg"})
        target1 = Flow.from_dict({"name": "B", "context": "air", "unit": "kg"})
        target2 = Flow.from_dict({"name": "C", "context": "air", "unit": "kg"})

        match1 = Match(
            source=source,
            target=target1,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=True,
        )
        match2 = Match(
            source=source,
            target=target2,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=False,
        )

        assert (
            match1 < match2
        ), "Expected match1 to be less than match2 based on target name"

    def test_match_comparison_new_target_flow_does_not_affect_sorting(self):
        """Test that new_target_flow does not affect comparison."""
        source1 = Flow.from_dict({"name": "A", "context": "air", "unit": "kg"})
        target1 = Flow.from_dict({"name": "B", "context": "air", "unit": "kg"})
        source2 = Flow.from_dict({"name": "C", "context": "air", "unit": "kg"})
        target2 = Flow.from_dict({"name": "D", "context": "air", "unit": "kg"})

        match1 = Match(
            source=source1,
            target=target1,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=True,
        )
        match2 = Match(
            source=source2,
            target=target2,
            function_name="test",
            condition=MatchCondition.exact,
            new_target_flow=False,
        )

        # Comparison should be based on source/target names, not new_target_flow
        assert (
            match1 < match2
        ), "Expected comparison based on names, not new_target_flow"


class TestMatchWithComplexFlows:
    """Test Match with complex flow data."""

    def test_match_with_all_flow_fields(self):
        """Test Match with flows containing all possible fields."""
        source_flow = Flow.from_dict(
            {
                "name": "Carbon dioxide, in air",
                "context": ["Emissions", "to air"],
                "unit": "kg",
                "identifier": "source-id",
                "location": "US",
                "cas_number": "000124-38-9",
                "synonyms": ["CO2"],
            }
        )
        target_flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": ["Emissions", "to air"],
                "unit": "kg",
                "identifier": "target-id",
                "location": "CA",
                "cas_number": "124-38-9",
            }
        )

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.close,
            conversion_factor=1.5,
            comment="Complex match",
            new_target_flow=True,
        )

        assert match.source == source_flow
        assert match.target == target_flow
        assert match.new_target_flow is True

        exported = match.export()
        assert exported["new_target_flow"] is True
        assert exported["conversion_factor"] == 1.5
        assert exported["comment"] == "Complex match"


class TestMatchExportEdgeCases:
    """Test Match export edge cases."""

    def test_export_excludes_private_attributes(self):
        """Test export excludes _id and other private attributes."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        exported = match.export()

        # Check source and target don't have _id
        assert "_id" not in exported["source"], "Expected _id not in exported source"
        assert "_id" not in exported["target"], "Expected _id not in exported target"

    def test_export_with_flowmapper_metadata_true(self):
        """Test export with flowmapper_metadata=True includes version."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        exported = match.export(flowmapper_metadata=True)

        assert (
            "flowmapper_metadata" in exported
        ), "Expected flowmapper_metadata in export"
        assert (
            "version" in exported["flowmapper_metadata"]
        ), "Expected version in metadata"
        assert (
            "function_name" in exported["flowmapper_metadata"]
        ), "Expected function_name in metadata"
        assert (
            exported["flowmapper_metadata"]["function_name"] == "test_function"
        ), "Expected function_name to match"

    def test_export_with_flowmapper_metadata_false(self):
        """Test export with flowmapper_metadata=False excludes metadata."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        exported = match.export(flowmapper_metadata=False)

        assert (
            "flowmapper_metadata" not in exported
        ), "Expected flowmapper_metadata not in export"

    def test_export_serializes_userstring_objects(self):
        """Test export serializes UserString objects in source/target."""
        from flowmapper.fields import StringField

        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        exported = match.export()

        # StringField is a UserString subclass, should be serialized to string
        assert isinstance(
            exported["source"]["name"], str
        ), "Expected name to be string, not UserString"
        assert isinstance(
            exported["target"]["name"], str
        ), "Expected name to be string, not UserString"

    def test_export_serializes_contextfield_objects(self):
        """Test export serializes ContextField objects."""
        source_flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": ["air", "unspecified"], "unit": "kg"}
        )
        target_flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})

        match = Match(
            source=source_flow,
            target=target_flow,
            function_name="test_function",
            condition=MatchCondition.exact,
        )

        exported = match.export()

        # ContextField should be serialized to its value
        assert isinstance(
            exported["source"]["context"], (str, tuple, list)
        ), "Expected context to be serialized"
        assert not hasattr(
            exported["source"]["context"], "value"
        ), "Expected context not to be ContextField object"
