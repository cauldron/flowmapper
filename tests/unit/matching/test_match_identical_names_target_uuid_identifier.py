"""Unit tests for match_identical_names_target_uuid_identifier function."""

from copy import copy

import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.matching.basic import match_identical_names_target_uuid_identifier


class TestMatchIdenticalNamesTargetUuidIdentifier:
    """Test match_identical_names_target_uuid_identifier function."""

    def test_basic_matching_with_uuid_identifier(self):
        """Test basic matching when target has valid UUID identifier."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 1, "Expected one match"
        assert matches[0].source == source_flow, "Expected source to match"
        assert matches[0].target == target_flow, "Expected target to match"
        assert (
            matches[0].condition == MatchCondition.exact
        ), "Expected condition to be exact"
        assert (
            matches[0].function_name == "match_identical_names_target_uuid_identifier"
        ), "Expected correct function name"

    def test_no_match_when_target_has_no_identifier(self):
        """Test that no match occurs when target has no identifier."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            # No identifier
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no match when target has no identifier"

    def test_no_match_when_target_identifier_not_uuid(self):
        """Test that no match occurs when target identifier is not a UUID."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "not-a-uuid",  # Not a valid UUID
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert (
            len(matches) == 0
        ), "Expected no match when target identifier is not a UUID"

    def test_no_match_when_names_differ(self):
        """Test that no match occurs when names differ."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Methane",  # Different name
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no match when names differ"

    def test_no_match_when_contexts_differ(self):
        """Test that no match occurs when contexts differ."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "water",  # Different context
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no match when contexts differ"

    def test_no_match_when_locations_differ(self):
        """Test that no match occurs when locations differ."""
        source_data = {
            "name": "Carbon dioxide, NL",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide, DE",  # Different location
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no match when locations differ"

    def test_no_match_when_oxidation_states_differ(self):
        """Test that no match occurs when oxidation states differ."""
        source_data = {
            "name": "Iron(II) oxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Iron(III) oxide",  # Different oxidation state
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no match when oxidation states differ"

    def test_matches_with_custom_function_name(self):
        """Test that custom function_name parameter is used."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf],
            target_flows=[target_nf],
            function_name="custom_function",
        )

        assert len(matches) == 1, "Expected one match"
        assert (
            matches[0].function_name == "custom_function"
        ), "Expected custom function name"

    def test_matches_with_custom_comment(self):
        """Test that custom comment parameter is used."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf],
            target_flows=[target_nf],
            comment="Custom comment",
        )

        assert len(matches) == 1, "Expected one match"
        assert matches[0].comment == "Custom comment", "Expected custom comment"

    def test_matches_with_custom_match_condition(self):
        """Test that custom match_condition parameter is used."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf],
            target_flows=[target_nf],
            match_condition=MatchCondition.related,
        )

        assert len(matches) == 1, "Expected one match"
        assert (
            matches[0].condition == MatchCondition.related
        ), "Expected custom match condition"

    def test_multiple_source_flows_same_group(self):
        """Test matching multiple source flows in the same group."""
        source_flows = []
        for i in range(3):
            source_data = {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
            }
            source_flow = Flow.from_dict(source_data)
            source_normalized = source_flow.normalize()
            source_nf = NormalizedFlow(
                original=source_flow,
                normalized=source_normalized,
                current=copy(source_normalized),
            )
            source_flows.append(source_nf)

        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=source_flows, target_flows=[target_nf]
        )

        assert len(matches) == 3, "Expected three matches for three source flows"

    def test_filters_targets_without_uuid(self):
        """Test that only targets with UUID identifiers are considered."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        # Target with UUID - should match
        target1_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target1_flow = Flow.from_dict(target1_data)
        target1_normalized = target1_flow.normalize()
        target1_nf = NormalizedFlow(
            original=target1_flow,
            normalized=target1_normalized,
            current=copy(target1_normalized),
        )

        # Target without identifier - should not match
        target2_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        target2_flow = Flow.from_dict(target2_data)
        target2_normalized = target2_flow.normalize()
        target2_nf = NormalizedFlow(
            original=target2_flow,
            normalized=target2_normalized,
            current=copy(target2_normalized),
        )

        # Target with non-UUID identifier - should not match
        target3_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "not-a-uuid",
        }
        target3_flow = Flow.from_dict(target3_data)
        target3_normalized = target3_flow.normalize()
        target3_nf = NormalizedFlow(
            original=target3_flow,
            normalized=target3_normalized,
            current=copy(target3_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf],
            target_flows=[target1_nf, target2_nf, target3_nf],
        )

        assert len(matches) == 1, "Expected one match (only target with UUID)"
        assert matches[0].target == target1_flow, "Expected match with UUID target"

    def test_uuid_format_validation(self):
        """Test that UUID format is strictly validated."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        # Invalid UUID formats that should not match
        invalid_identifiers = [
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400e29b41d4a716446655440000",  # Missing hyphens
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid character
            "550E8400-E29B-41D4-A716-446655440000",  # Uppercase (should work but let's test)
        ]

        for invalid_id in invalid_identifiers:
            target_data = {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": invalid_id,
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )

            matches = match_identical_names_target_uuid_identifier(
                source_flows=[source_nf], target_flows=[target_nf]
            )

            # Note: Uppercase UUIDs should actually match (regex allows A-F)
            if invalid_id == "550E8400-E29B-41D4-A716-446655440000":
                assert (
                    len(matches) == 1
                ), f"Expected match for uppercase UUID: {invalid_id}"
            else:
                assert (
                    len(matches) == 0
                ), f"Expected no match for invalid UUID format: {invalid_id}"

    def test_unit_compatibility_required(self):
        """Test that only unit-compatible flows are matched."""
        source_data = {
            "name": "Water",
            "context": "water",
            "unit": "m3",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        target_data = {
            "name": "Water",
            "context": "water",
            "unit": "kg",  # Incompatible unit
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[target_nf]
        )

        # get_matches filters by unit compatibility
        assert len(matches) == 0, "Expected no match for incompatible units"

    def test_empty_source_flows(self):
        """Test with empty source flows list."""
        target_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "550e8400-e29b-41d4-a716-446655440000",
        }
        target_flow = Flow.from_dict(target_data)
        target_normalized = target_flow.normalize()
        target_nf = NormalizedFlow(
            original=target_flow,
            normalized=target_normalized,
            current=copy(target_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[], target_flows=[target_nf]
        )

        assert len(matches) == 0, "Expected no matches with empty source flows"

    def test_empty_target_flows(self):
        """Test with empty target flows list."""
        source_data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        source_flow = Flow.from_dict(source_data)
        source_normalized = source_flow.normalize()
        source_nf = NormalizedFlow(
            original=source_flow,
            normalized=source_normalized,
            current=copy(source_normalized),
        )

        matches = match_identical_names_target_uuid_identifier(
            source_flows=[source_nf], target_flows=[]
        )

        assert len(matches) == 0, "Expected no matches with empty target flows"
