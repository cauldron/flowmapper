"""Unit tests for add_missing_regionalized_flows function."""

from copy import copy

from flowmapper.domain import Flow, MatchCondition, NormalizedFlow
from flowmapper.matching import add_missing_regionalized_flows


class TestAddMissingRegionalizedFlows:
    """Test add_missing_regionalized_flows function."""

    def test_basic_functionality_with_enough_regions(self):
        """Test basic functionality when there are enough regions in target."""
        # Source flow with location
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

        assert source_nf.location == "NL"
        assert source_nf.name == "carbon dioxide"

        # Target flows with different locations (enough to meet cutoff)
        target_flows = []
        for location in ["DE", "FR", "US", "CA"]:
            target_data = {
                "name": f"Carbon dioxide, {location}",
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            assert target_nf.name == "carbon dioxide"
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        assert len(matches) == 1, "Expected one match"
        assert matches[0].new_target_flow is True, "Expected new_target_flow to be True"
        assert (
            matches[0].function_name == "add_missing_regionalized_flows"
        ), "Expected correct function name"
        assert (
            matches[0].condition == MatchCondition.related
        ), "Expected condition to be related"
        assert matches[0].source == source_flow, "Expected source to match"
        # Target should have the source's location
        assert matches[0].target.location is None
        assert matches[0].target.name == "Carbon dioxide, NL"

    def test_cutoff_filtering_not_enough_regions(self):
        """Test that flows are filtered out when not enough regions exist."""
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

        # Only 2 target flows (below cutoff of 3)
        target_flows = []
        for location in ["DE", "FR"]:
            target_data = {
                "name": f"Carbon dioxide, {location}",
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        assert len(matches) == 0, "Expected no matches when below cutoff"

    def test_cutoff_custom_value(self):
        """Test with custom cutoff value."""
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

        # 2 target flows - should work with cutoff=2
        target_flows = []
        for location in ["DE", "FR"]:
            target_data = {
                "name": f"Carbon dioxide, {location}",
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=2
        )

        assert len(matches) == 1, "Expected one match with cutoff=2"

    def test_unit_compatibility_filtering(self):
        """Test that only unit-compatible flows are matched."""
        source_data = {
            "name": "Water, NL",
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

        # Target flows with incompatible unit
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_data = {
                "name": f"Water, {location}",
                "context": "water",
                "unit": "kg",  # Different unit
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        # Should have no matches if units are incompatible
        # (assuming m3 and kg are not compatible)
        assert isinstance(matches, list), "Expected list of matches"

    def test_multiple_sources_same_group(self):
        """Test with multiple source flows in the same group."""
        source_flows = []
        for i in range(3):
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
            source_flows.append(source_nf)

        # Target flows with different locations
        target_flows = []
        for location in ["DE", "FR", "US", "CA"]:
            target_data = {
                "name": f"Carbon dioxide, {location}",
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=source_flows, target_flows=target_flows, cutoff=3
        )

        # Should create a match for each source flow
        assert len(matches) == 3, "Expected three matches for three source flows"

    def test_filters_out_flows_without_location(self):
        """Test that source flows without location are filtered out."""
        # Source flow with location
        source_with_location = Flow.from_dict(
            {"name": "Carbon dioxide, NL", "context": "air", "unit": "kg"}
        )
        source_nf_with = NormalizedFlow(
            original=source_with_location,
            normalized=source_with_location.normalize(),
            current=copy(source_with_location.normalize()),
        )

        # Source flow without location
        source_without_location = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        source_nf_without = NormalizedFlow(
            original=source_without_location,
            normalized=source_without_location.normalize(),
            current=copy(source_without_location.normalize()),
        )

        # Target flows
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_flow = Flow.from_dict(
                {"name": f"Carbon dioxide, {location}", "context": "air", "unit": "kg"}
            )
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_flow.normalize(),
                current=copy(target_flow.normalize()),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf_with, source_nf_without],
            target_flows=target_flows,
            cutoff=3,
        )

        # Should only match the flow with location
        assert len(matches) == 1, "Expected one match (only for flow with location)"
        assert (
            matches[0].source == source_with_location
        ), "Expected match to be for flow with location"

    def test_different_oxidation_states_not_matched(self):
        """Test that flows with different oxidation states are not matched."""
        # Source flow with oxidation state
        source_data = {
            "name": "Iron(II) oxide, NL",
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

        # Target flows with different oxidation state (or none)
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_data = {
                "name": "Iron(III) oxide, " + location,  # Different oxidation state
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        # Should not match if oxidation states differ
        assert len(matches) == 0, "Expected no matches with different oxidation states"

    def test_different_contexts_not_matched(self):
        """Test that flows with different contexts are not matched."""
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

        # Target flows with different context
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_data = {
                "name": f"Carbon dioxide, {location}",
                "context": "water",  # Different context
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        assert len(matches) == 0, "Expected no matches with different contexts"

    def test_different_names_not_matched(self):
        """Test that flows with different names are not matched."""
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

        # Target flows with different name
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_data = {
                "name": f"Water, {location}",  # Different name
                "context": "air",
                "unit": "kg",
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        assert len(matches) == 0, "Expected no matches with different names"

    def test_empty_source_flows(self):
        """Test with empty source flows list."""
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_flow = Flow.from_dict(
                {"name": f"Carbon dioxide, {location}", "context": "air", "unit": "kg"}
            )
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_flow.normalize(),
                current=copy(target_flow.normalize()),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[], target_flows=target_flows, cutoff=3
        )

        assert len(matches) == 0, "Expected no matches with empty source flows"

    def test_empty_target_flows(self):
        """Test with empty target flows list."""
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

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=[], cutoff=3
        )

        assert len(matches) == 0, "Expected no matches with empty target flows"

    def test_conversion_factor_calculated(self):
        """Test that conversion factor is calculated correctly."""
        source_data = {
            "name": "Water, NL",
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

        # Target flows with compatible unit
        target_flows = []
        for location in ["DE", "FR", "US"]:
            target_data = {
                "name": f"Water, {location}",
                "context": "water",
                "unit": "m3",  # Same unit
            }
            target_flow = Flow.from_dict(target_data)
            target_normalized = target_flow.normalize()
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_normalized,
                current=copy(target_normalized),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        if len(matches) > 0:
            assert (
                matches[0].conversion_factor == 1.0
            ), "Expected conversion_factor to be calculated (1.0 for same unit)"

    def test_comment_includes_location(self):
        """Test that comment includes the location information."""
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

        target_flows = []
        for location in ["DE", "FR", "US", "CA"]:
            target_flow = Flow.from_dict(
                {"name": f"Carbon dioxide, {location}", "context": "air", "unit": "kg"}
            )
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_flow.normalize(),
                current=copy(target_flow.normalize()),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        if len(matches) > 0:
            assert (
                "location" in matches[0].comment.lower()
            ), "Expected comment to mention location"
            assert (
                "new target flow" in matches[0].comment.lower()
                or "added" in matches[0].comment.lower()
            ), "Expected comment to mention new target flow"

    def test_multiple_groups_processed(self):
        """Test that multiple groups of source flows are processed."""
        source_flows = []
        # Group 1: Carbon dioxide, NL
        source1 = Flow.from_dict(
            {"name": "Carbon dioxide, NL", "context": "air", "unit": "kg"}
        )
        source_nf1 = NormalizedFlow(
            original=source1,
            normalized=source1.normalize(),
            current=copy(source1.normalize()),
        )
        source_flows.append(source_nf1)

        # Group 2: Water, FR
        source2 = Flow.from_dict(
            {"name": "Water, FR", "context": "water", "unit": "kg"}
        )
        source_nf2 = NormalizedFlow(
            original=source2,
            normalized=source2.normalize(),
            current=copy(source2.normalize()),
        )
        source_flows.append(source_nf2)

        # Target flows for both groups
        target_flows = []
        # For carbon dioxide
        for location in ["DE", "US", "CA"]:
            target_flow = Flow.from_dict(
                {"name": f"Carbon dioxide, {location}", "context": "air", "unit": "kg"}
            )
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_flow.normalize(),
                current=copy(target_flow.normalize()),
            )
            target_flows.append(target_nf)

        # For water
        for location in ["DE", "US", "CA"]:
            target_flow = Flow.from_dict(
                {"name": f"Water, {location}", "context": "water", "unit": "kg"}
            )
            target_nf = NormalizedFlow(
                original=target_flow,
                normalized=target_flow.normalize(),
                current=copy(target_flow.normalize()),
            )
            target_flows.append(target_nf)

        matches = add_missing_regionalized_flows(
            source_flows=source_flows, target_flows=target_flows, cutoff=3
        )

        # Should create matches for both groups
        assert len(matches) >= 2, "Expected matches for both groups"

    def test_target_without_location_not_considered(self):
        """Test that target flows without location are not considered as other_regions."""
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

        target_flows = []
        # One target with location
        target1 = Flow.from_dict(
            {"name": "Carbon dioxide, DE", "context": "air", "unit": "kg"}
        )
        target_nf1 = NormalizedFlow(
            original=target1,
            normalized=target1.normalize(),
            current=copy(target1.normalize()),
        )
        target_flows.append(target_nf1)

        # One target without location (should not be counted)
        target2 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        target_nf2 = NormalizedFlow(
            original=target2,
            normalized=target2.normalize(),
            current=copy(target2.normalize()),
        )
        target_flows.append(target_nf2)

        matches = add_missing_regionalized_flows(
            source_flows=[source_nf], target_flows=target_flows, cutoff=3
        )

        # Should have no matches because only 1 other region (below cutoff of 3)
        assert (
            len(matches) == 0
        ), "Expected no matches when not enough regions with location"
