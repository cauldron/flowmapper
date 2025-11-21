"""Unit tests for match_names_with_suffix_removal function."""

from copy import copy

import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.matching.specialized import match_names_with_suffix_removal


class TestMatchNamesWithSuffixRemoval:
    """Test match_names_with_suffix_removal function."""

    def test_matches_with_in_air_suffix(self):
        """Test matching flows where one has ', in air' suffix."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1
        assert matches[0].source == source.original
        assert matches[0].target == target.original
        assert matches[0].condition == MatchCondition.close
        assert matches[0].function_name == "match_names_with_suffix_removal"

    def test_matches_with_in_ground_suffix(self):
        """Test matching flows where one has ', in ground' suffix."""
        source = NormalizedFlow.from_dict(
            {"name": "Methane, in ground", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Methane", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_with_ion_suffix(self):
        """Test matching flows where one has ', ion' suffix."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, ion", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_biogenic_to_non_fossil(self):
        """Test matching biogenic to non-fossil flows."""
        source = NormalizedFlow.from_dict(
            {"name": "Methane, biogenic", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Methane, non-fossil", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_requires_matching_context(self):
        """Test that flows must have matching context."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "water",  # Different context
                "unit": "kg",
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 0

    def test_requires_matching_oxidation_state(self):
        """Test that flows must have matching oxidation state."""
        # Create flows with different oxidation states by using names that
        # will be parsed differently
        source = NormalizedFlow.from_dict(
            {"name": "Iron(II), in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Iron(III)",  # Different oxidation state (III vs II)
                "context": "air",
                "unit": "kg",
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 0

    def test_requires_matching_location(self):
        """Test that flows must have matching location."""
        source = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide, in air",
                "context": "air",
                "unit": "kg",
                "location": "NL",
            }
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "location": "DE",  # Different location
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 0

    def test_matches_with_matching_location(self):
        """Test that flows with matching location are matched."""
        source = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide, in air",
                "context": "air",
                "unit": "kg",
                "location": "NL",
            }
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "location": "NL",  # Same location
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_with_none_location(self):
        """Test that flows with None location match."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_requires_unit_compatibility(self):
        """Test that flows must be unit-compatible."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "m3",  # Incompatible unit
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 0

    def test_matches_multiple_sources_same_group(self):
        """Test matching multiple source flows in the same group."""
        source1 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        source2 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source1, source2], target_flows=[target]
        )

        assert len(matches) == 2

    def test_matches_multiple_targets(self):
        """Test matching when multiple target flows match."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target1 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target2 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target1, target2]
        )

        # get_matches only creates matches when exactly one target remains
        # after filtering. If multiple targets match and have the same context,
        # no match is created (to avoid ambiguity)
        # In this case, both targets have the same context, so no match is created
        assert len(matches) == 0

    def test_case_insensitive_name_matching(self):
        """Test that name matching is case-insensitive."""
        source = NormalizedFlow.from_dict(
            {
                "name": "Carbon Dioxide, in air",  # Mixed case
                "context": "air",
                "unit": "kg",
            }
        )
        target = NormalizedFlow.from_dict(
            {"name": "carbon dioxide", "context": "air", "unit": "kg"}  # Lowercase
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_custom_function_name(self):
        """Test that custom function_name is used."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source],
            target_flows=[target],
            function_name="custom_match_function",
        )

        assert matches[0].function_name == "custom_match_function"

    def test_custom_comment(self):
        """Test that custom comment is used."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target], comment="Custom comment"
        )

        assert matches[0].comment == "Custom comment"

    def test_custom_match_condition(self):
        """Test that custom match_condition is used."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source],
            target_flows=[target],
            match_condition=MatchCondition.exact,
        )

        assert matches[0].condition == MatchCondition.exact

    def test_no_match_when_names_not_equivalent(self):
        """Test that flows with non-equivalent names don't match."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {
                "name": "Carbon monoxide",  # Different base name
                "context": "air",
                "unit": "kg",
            }
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 0

    def test_matches_with_unspecified_origin_suffix(self):
        """Test matching flows with ', unspecified origin' suffix."""
        source = NormalizedFlow.from_dict(
            {"name": "Methane, unspecified origin", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Methane", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_with_in_water_suffix(self):
        """Test matching flows with ', in water' suffix."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in water", "context": "water", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "water", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_reverse_direction(self):
        """Test matching when target has suffix and source doesn't."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1

    def test_matches_multiple_different_groups(self):
        """Test matching multiple groups of flows."""
        source1 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        source2 = NormalizedFlow.from_dict(
            {"name": "Methane, in ground", "context": "air", "unit": "kg"}
        )
        target1 = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target2 = NormalizedFlow.from_dict(
            {"name": "Methane", "context": "air", "unit": "kg"}
        )

        matches = match_names_with_suffix_removal(
            source_flows=[source1, source2], target_flows=[target1, target2]
        )

        assert len(matches) == 2

    def test_marked_as_matched(self):
        """Test that matched source flows are marked as matched."""
        source = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide, in air", "context": "air", "unit": "kg"}
        )
        target = NormalizedFlow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert source.matched is False

        matches = match_names_with_suffix_removal(
            source_flows=[source], target_flows=[target]
        )

        assert len(matches) == 1
        assert source.matched is True
