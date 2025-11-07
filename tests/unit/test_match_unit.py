"""Unit tests for match.py functions using mocks."""

from unittest.mock import MagicMock, Mock

import pytest

from flowmapper.match import (
    format_match_result,
    match_identical_identifier,
    match_identical_names,
    match_identical_names_without_commas,
    match_resources_with_wrong_subcontext,
)


class TestFormatMatchResult:
    """Unit tests for format_match_result function."""

    def test_format_match_result_with_all_fields(self):
        """Test format_match_result with all fields."""
        # Create mock Flow objects
        source_flow = Mock()
        source_flow.export = {"name": "Source", "context": ["air"], "unit": "kg"}

        target_flow = Mock()
        target_flow.export = {"name": "Target", "context": ["air"], "unit": "kg"}

        match_info = {"comment": "Test match", "confidence": 0.95}
        conversion_factor = 1.0

        result = format_match_result(source_flow, target_flow, conversion_factor, match_info)

        assert result["source"] == source_flow.export
        assert result["target"] == target_flow.export
        assert result["conversion_factor"] == conversion_factor
        assert result["comment"] == "Test match"
        assert result["confidence"] == 0.95

    def test_format_match_result_merges_match_info(self):
        """Test that format_match_result properly merges match_info."""
        source_flow = Mock()
        source_flow.export = {"name": "Source"}

        target_flow = Mock()
        target_flow.export = {"name": "Target"}

        match_info = {"comment": "Match", "extra_field": "value"}
        result = format_match_result(source_flow, target_flow, 2.5, match_info)

        assert result["extra_field"] == "value"
        assert result["conversion_factor"] == 2.5


class TestMatchIdenticalIdentifier:
    """Unit tests for match_identical_identifier function."""

    def test_match_identical_identifier_when_identical(self):
        """Test match when identifiers are identical."""
        source_flow = Mock()
        source_flow.identifier = "test-id-123"

        target_flow = Mock()
        target_flow.identifier = "test-id-123"

        result = match_identical_identifier(source_flow, target_flow, [], [])

        assert result == {"comment": "Identical identifier"}

    def test_match_identical_identifier_when_different(self):
        """Test match when identifiers are different."""
        source_flow = Mock()
        source_flow.identifier = "test-id-123"

        target_flow = Mock()
        target_flow.identifier = "test-id-456"

        result = match_identical_identifier(source_flow, target_flow, [], [])

        assert result is None

    def test_match_identical_identifier_when_source_missing(self):
        """Test match when source identifier is missing."""
        source_flow = Mock()
        source_flow.identifier = None

        target_flow = Mock()
        target_flow.identifier = "test-id-123"

        result = match_identical_identifier(source_flow, target_flow, [], [])

        assert result is None

    def test_match_identical_identifier_with_custom_comment(self):
        """Test match with custom comment."""
        source_flow = Mock()
        source_flow.identifier = "test-id-123"

        target_flow = Mock()
        target_flow.identifier = "test-id-123"

        result = match_identical_identifier(source_flow, target_flow, [], [], comment="Custom comment")

        assert result == {"comment": "Custom comment"}


class TestMatchIdenticalNames:
    """Unit tests for match_identical_names function."""

    def test_match_identical_names_when_identical(self):
        """Test match when names and contexts are identical."""
        source_flow = Mock()
        source_flow.name = "Water"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name = "Water"
        target_flow.context = ["air"]

        result = match_identical_names(source_flow, target_flow, [], [])

        assert result == {"comment": "Identical names"}

    def test_match_identical_names_when_names_different(self):
        """Test match when names are different."""
        source_flow = Mock()
        source_flow.name = "Water"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name = "Air"
        target_flow.context = ["air"]

        result = match_identical_names(source_flow, target_flow, [], [])

        assert result is None

    def test_match_identical_names_when_contexts_different(self):
        """Test match when contexts are different."""
        source_flow = Mock()
        source_flow.name = "Water"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name = "Water"
        target_flow.context = ["ground"]

        result = match_identical_names(source_flow, target_flow, [], [])

        assert result is None


class TestMatchIdenticalNamesWithoutCommas:
    """Unit tests for match_identical_names_without_commas function."""

    def test_match_identical_names_without_commas_when_identical(self):
        """Test match when names are identical after removing commas."""
        source_flow = Mock()
        source_flow.name.normalized = "Water, pure"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name.normalized = "Water pure"
        target_flow.context = ["air"]

        result = match_identical_names_without_commas(source_flow, target_flow, [], [])

        assert result == {"comment": "Identical names when commas removed"}

    def test_match_identical_names_without_commas_when_different(self):
        """Test match when names are different even after removing commas."""
        source_flow = Mock()
        source_flow.name.normalized = "Water, pure"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name.normalized = "Air, pure"
        target_flow.context = ["air"]

        result = match_identical_names_without_commas(source_flow, target_flow, [], [])

        assert result is None

    def test_match_identical_names_without_commas_when_contexts_different(self):
        """Test match when contexts are different."""
        source_flow = Mock()
        source_flow.name.normalized = "Water, pure"
        source_flow.context = ["air"]

        target_flow = Mock()
        target_flow.name.normalized = "Water pure"
        target_flow.context = ["ground"]

        result = match_identical_names_without_commas(source_flow, target_flow, [], [])

        assert result is None


class TestMatchResourcesWithWrongSubcontext:
    """Unit tests for match_resources_with_wrong_subcontext function."""

    def test_match_resources_with_wrong_subcontext_when_matching(self):
        """Test match when resources have identical names but wrong subcontext."""
        source_flow = Mock()
        source_flow.context.normalized = ["natural resource", "in ground"]
        source_flow.name = "Copper"

        target_flow = Mock()
        target_flow.context.normalized = ["natural resource", "in air"]
        target_flow.name = "Copper"

        result = match_resources_with_wrong_subcontext(source_flow, target_flow, [], [])

        assert result == {"comment": "Resources with identical name but wrong subcontext"}

    def test_match_resources_with_wrong_subcontext_when_names_different(self):
        """Test match when names are different."""
        source_flow = Mock()
        source_flow.context.normalized = ["natural resource", "in ground"]
        source_flow.name = "Copper"

        target_flow = Mock()
        target_flow.context.normalized = ["natural resource", "in air"]
        target_flow.name = "Iron"

        result = match_resources_with_wrong_subcontext(source_flow, target_flow, [], [])

        assert result is None

    def test_match_resources_with_wrong_subcontext_when_not_resources(self):
        """Test match when flows are not resources."""
        source_flow = Mock()
        source_flow.context.normalized = ["emission", "to air"]
        source_flow.name = "CO2"

        target_flow = Mock()
        target_flow.context.normalized = ["emission", "to air"]
        target_flow.name = "CO2"

        result = match_resources_with_wrong_subcontext(source_flow, target_flow, [], [])

        assert result is None

    def test_match_resources_with_wrong_subcontext_case_insensitive(self):
        """Test match with case-insensitive resource category matching."""
        source_flow = Mock()
        source_flow.context.normalized = ["NATURAL RESOURCE", "in ground"]
        source_flow.name = "Copper"

        target_flow = Mock()
        target_flow.context.normalized = ["natural resource", "in air"]
        target_flow.name = "Copper"

        result = match_resources_with_wrong_subcontext(source_flow, target_flow, [], [])

        assert result == {"comment": "Resources with identical name but wrong subcontext"}

    def test_match_resources_with_wrong_subcontext_one_not_resource(self):
        """Test match when only one flow is a resource."""
        source_flow = Mock()
        source_flow.context.normalized = ["natural resource", "in ground"]
        source_flow.name = "Copper"

        target_flow = Mock()
        target_flow.context.normalized = ["emission", "to air"]
        target_flow.name = "Copper"

        result = match_resources_with_wrong_subcontext(source_flow, target_flow, [], [])

        assert result is None

