"""Unit tests for Flowmap class using mocks."""

from copy import copy
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.match import Match
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.flowmap import Flowmap


class TestFlowmapInit:
    """Test Flowmap __init__ method."""

    @patch("flowmapper.flowmap.match_rules")
    def test_init_with_default_rules(self, mock_match_rules):
        """Test initialization with default rules."""
        mock_rules = [Mock(), Mock()]
        mock_match_rules.return_value = mock_rules

        source_flows = [Mock(spec=NormalizedFlow)]
        target_flows = [Mock(spec=NormalizedFlow)]
        data_prep_funcs = [Mock()]

        flowmap = Flowmap(
            source_flows=source_flows,
            target_flows=target_flows,
            data_preparation_functions=data_prep_funcs,
        )

        assert flowmap.source_flows == source_flows
        assert flowmap.target_flows == target_flows
        assert flowmap.data_preparation_functions == data_prep_funcs
        assert flowmap.rules == mock_rules
        assert flowmap.matches == []
        assert flowmap.show_progressbar is True
        mock_match_rules.assert_called_once()

    def test_init_with_custom_rules(self):
        """Test initialization with custom rules."""
        source_flows = [Mock(spec=NormalizedFlow)]
        target_flows = [Mock(spec=NormalizedFlow)]
        data_prep_funcs = [Mock()]
        custom_rules = [Mock(), Mock()]

        flowmap = Flowmap(
            source_flows=source_flows,
            target_flows=target_flows,
            data_preparation_functions=data_prep_funcs,
            rules=custom_rules,
        )

        assert flowmap.rules == custom_rules

    def test_init_with_show_progressbar_false(self):
        """Test initialization with show_progressbar=False."""
        source_flows = [Mock(spec=NormalizedFlow)]
        target_flows = [Mock(spec=NormalizedFlow)]
        data_prep_funcs = [Mock()]

        flowmap = Flowmap(
            source_flows=source_flows,
            target_flows=target_flows,
            data_preparation_functions=data_prep_funcs,
            show_progressbar=False,
        )

        assert flowmap.show_progressbar is False


class TestFlowmapGenerateMatches:
    """Test Flowmap generate_matches method."""

    @patch("flowmapper.flowmap.logger")
    @patch("flowmapper.flowmap.time")
    def test_generate_matches_applies_rules(self, mock_time, mock_logger):
        """Test that generate_matches applies all rules."""
        # time() is called once per rule for start time, then again for elapsed
        # Provide enough values: start1, end1, start2, end2
        mock_time.side_effect = [0.0, 1.0, 1.0, 2.0]

        # Create mock flows
        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.matched = False
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.matched = False
        target_flow = Mock(spec=NormalizedFlow)

        # Create mock matches
        match1 = Mock(spec=Match)
        match1.new_target_flow = False
        match2 = Mock(spec=Match)
        match2.new_target_flow = False

        # Create mock rules
        rule1 = Mock()
        rule1.__name__ = "rule1"
        rule1.return_value = [match1]

        rule2 = Mock()
        rule2.__name__ = "rule2"
        rule2.return_value = [match2]

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2],
            target_flows=[target_flow],
            data_preparation_functions=[],
            rules=[rule1, rule2],
        )

        flowmap.generate_matches()

        # Verify rules were called with unmatched flows
        assert rule1.called
        assert rule2.called
        assert len(flowmap.matches) == 2
        assert flowmap.matches == [match1, match2]

    @patch("flowmapper.flowmap.logger")
    @patch("flowmapper.flowmap.time")
    def test_generate_matches_filters_matched_flows(self, mock_time, mock_logger):
        """Test that generate_matches only passes unmatched flows to rules."""
        mock_time.side_effect = [0.0, 1.0]

        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.matched = False
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.matched = True  # Already matched
        target_flow = Mock(spec=NormalizedFlow)

        rule = Mock()
        rule.__name__ = "test_rule"
        rule.return_value = []

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2],
            target_flows=[target_flow],
            data_preparation_functions=[],
            rules=[rule],
        )

        flowmap.generate_matches()

        # Verify rule was called with only unmatched flow
        rule.assert_called_once()
        call_args = rule.call_args
        assert len(call_args.kwargs["source_flows"]) == 1
        assert call_args.kwargs["source_flows"][0] == source_flow1

    @patch("flowmapper.flowmap.logger")
    @patch("flowmapper.flowmap.time")
    def test_generate_matches_adds_new_target_flows(self, mock_time, mock_logger):
        """Test that generate_matches adds new target flows when created."""
        mock_time.side_effect = [0.0, 1.0]

        source_flow = Mock(spec=NormalizedFlow)
        source_flow.matched = False
        target_flow = Mock(spec=NormalizedFlow)
        new_target_flow = Mock(spec=Flow)

        match = Mock(spec=Match)
        match.new_target_flow = True
        match.target = new_target_flow

        rule = Mock()
        rule.__name__ = "test_rule"
        rule.return_value = [match]

        flowmap = Flowmap(
            source_flows=[source_flow],
            target_flows=[target_flow],
            data_preparation_functions=[],
            rules=[rule],
        )

        # Mock the add_new_target_flows method
        flowmap.add_new_target_flows = Mock()

        flowmap.generate_matches()

        # Verify add_new_target_flows was called with new target flow
        flowmap.add_new_target_flows.assert_called_once_with([new_target_flow])

    @patch("flowmapper.flowmap.logger")
    @patch("flowmapper.flowmap.time")
    def test_generate_matches_logs_with_new_target_flows(self, mock_time, mock_logger):
        """Test that generate_matches logs correctly when new target flows are created."""
        mock_time.side_effect = [0.0, 1.0]

        source_flow = Mock(spec=NormalizedFlow)
        source_flow.matched = False
        target_flow = Mock(spec=NormalizedFlow)
        new_target_flow = Mock(spec=Flow)

        match = Mock(spec=Match)
        match.new_target_flow = True
        match.target = new_target_flow

        rule = Mock()
        rule.__name__ = "test_rule"
        rule.return_value = [match]

        flowmap = Flowmap(
            source_flows=[source_flow],
            target_flows=[target_flow],
            data_preparation_functions=[],
            rules=[rule],
        )
        flowmap.add_new_target_flows = Mock()

        flowmap.generate_matches()

        # Verify logger was called with message about new target flows
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "new target flows" in call_args.lower()
        assert "1" in call_args  # 1 new target flow

    @patch("flowmapper.flowmap.logger")
    @patch("flowmapper.flowmap.time")
    def test_generate_matches_logs_without_new_target_flows(
        self, mock_time, mock_logger
    ):
        """Test that generate_matches logs correctly when no new target flows."""
        mock_time.side_effect = [0.0, 1.0]

        source_flow = Mock(spec=NormalizedFlow)
        source_flow.matched = False
        target_flow = Mock(spec=NormalizedFlow)

        match = Mock(spec=Match)
        match.new_target_flow = False

        rule = Mock()
        rule.__name__ = "test_rule"
        rule.return_value = [match]

        flowmap = Flowmap(
            source_flows=[source_flow],
            target_flows=[target_flow],
            data_preparation_functions=[],
            rules=[rule],
        )

        flowmap.generate_matches()

        # Verify logger was called without mention of new target flows
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "new target flows" not in call_args.lower()


class TestFlowmapAddNewTargetFlows:
    """Test Flowmap add_new_target_flows method."""

    @patch(
        "flowmapper.flowmap.apply_transformation_and_convert_flows_to_normalized_flows"
    )
    def test_add_new_target_flows_normalizes_and_adds(self, mock_apply):
        """Test that add_new_target_flows normalizes flows and adds them."""
        new_flow1 = Mock(spec=Flow)
        new_flow2 = Mock(spec=Flow)

        normalized_flow1 = Mock(spec=NormalizedFlow)
        normalized_flow2 = Mock(spec=NormalizedFlow)
        mock_apply.return_value = [normalized_flow1, normalized_flow2]

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[Mock()],
        )

        flowmap.add_new_target_flows([new_flow1, new_flow2])

        # Verify flows were normalized
        mock_apply.assert_called_once_with(
            functions=flowmap.data_preparation_functions, flows=[new_flow1, new_flow2]
        )

        # Verify normalized flows were added
        assert len(flowmap.target_flows) == 2
        assert flowmap.target_flows == [normalized_flow1, normalized_flow2]


class TestFlowmapMatchedSource:
    """Test Flowmap matched_source method."""

    def test_matched_source_returns_matched_flows(self):
        """Test that matched_source returns only matched flows."""
        # Create flows with IDs
        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.id = 1
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.id = 2
        source_flow3 = Mock(spec=NormalizedFlow)
        source_flow3.id = 3

        # Create matches with source flows
        source_flow_for_match1 = Mock(spec=Flow)
        source_flow_for_match1._id = 1
        source_flow_for_match2 = Mock(spec=Flow)
        source_flow_for_match2._id = 2

        match1 = Mock(spec=Match)
        match1.source = source_flow_for_match1
        match2 = Mock(spec=Match)
        match2.source = source_flow_for_match2

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2, source_flow3],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        result = flowmap.matched_source()

        assert len(result) == 2
        assert source_flow1 in result
        assert source_flow2 in result
        assert source_flow3 not in result

    def test_matched_source_returns_empty_when_no_matches(self):
        """Test that matched_source returns empty list when no matches."""
        source_flow = Mock(spec=NormalizedFlow)
        source_flow.id = 1

        flowmap = Flowmap(
            source_flows=[source_flow],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        result = flowmap.matched_source()

        assert result == []


class TestFlowmapUnmatchedSource:
    """Test Flowmap unmatched_source property."""

    def test_unmatched_source_returns_unmatched_flows(self):
        """Test that unmatched_source returns only unmatched flows."""
        # Create flows with IDs
        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.id = 1
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.id = 2
        source_flow3 = Mock(spec=NormalizedFlow)
        source_flow3.id = 3

        # Create matches for flow1 and flow2
        source_flow_for_match1 = Mock(spec=Flow)
        source_flow_for_match1._id = 1
        source_flow_for_match2 = Mock(spec=Flow)
        source_flow_for_match2._id = 2

        match1 = Mock(spec=Match)
        match1.source = source_flow_for_match1
        match2 = Mock(spec=Match)
        match2.source = source_flow_for_match2

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2, source_flow3],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        result = flowmap.unmatched_source

        assert len(result) == 1
        assert source_flow3 in result
        assert source_flow1 not in result
        assert source_flow2 not in result

    def test_unmatched_source_returns_all_when_no_matches(self):
        """Test that unmatched_source returns all flows when no matches."""
        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.id = 1
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.id = 2

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        result = flowmap.unmatched_source

        assert len(result) == 2
        assert source_flow1 in result
        assert source_flow2 in result


class TestFlowmapMatchedSourceStatistics:
    """Test Flowmap matched_source_statistics method."""

    def test_matched_source_statistics_creates_dataframe(self):
        """Test that matched_source_statistics returns a DataFrame."""
        # Create flows with contexts
        context1 = Mock()
        context1.value = "air"
        context2 = Mock()
        context2.value = "water"

        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.original = Mock()
        source_flow1.original.context = context1
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.original = Mock()
        source_flow2.original.context = context2

        # Create matches
        match_context1 = Mock()
        match_context1.value = "air"
        match_context2 = Mock()
        match_context2.value = "air"

        match1 = Mock(spec=Match)
        match1.source = Mock()
        match1.source.context = match_context1
        match2 = Mock(spec=Match)
        match2.source = Mock()
        match2.source.context = match_context2

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        result = flowmap.matched_source_statistics()

        assert isinstance(result, pd.DataFrame)
        assert "context" in result.columns
        assert "matched" in result.columns
        assert "total" in result.columns
        assert "percent" in result.columns

    def test_matched_source_statistics_calculates_percentages(self):
        """Test that matched_source_statistics calculates correct percentages."""
        # Create flows with contexts
        air_context = Mock()
        air_context.value = "air"
        water_context = Mock()
        water_context.value = "water"

        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.original = Mock()
        source_flow1.original.context = air_context
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.original = Mock()
        source_flow2.original.context = air_context
        source_flow3 = Mock(spec=NormalizedFlow)
        source_flow3.original = Mock()
        source_flow3.original.context = water_context

        # Create match for one air flow
        match_air_context = Mock()
        match_air_context.value = "air"
        match1 = Mock(spec=Match)
        match1.source = Mock()
        match1.source.context = match_air_context

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2, source_flow3],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1]

        result = flowmap.matched_source_statistics()

        # Check air context: 1 matched, 2 total
        air_row = result[result["context"] == "air"].iloc[0]
        assert air_row["matched"] == 1
        assert air_row["total"] == 2
        assert air_row["percent"] == 0.5

        # Check water context: 0 matched, 1 total
        water_row = result[result["context"] == "water"].iloc[0]
        assert water_row["matched"] == 0
        assert water_row["total"] == 1
        assert water_row["percent"] == 0.0

    def test_matched_source_statistics_sorts_by_percent(self):
        """Test that matched_source_statistics sorts by percentage."""
        # Create flows with different contexts
        air_context = Mock()
        air_context.value = "air"
        water_context = Mock()
        water_context.value = "water"

        source_flow1 = Mock(spec=NormalizedFlow)
        source_flow1.original = Mock()
        source_flow1.original.context = air_context
        source_flow2 = Mock(spec=NormalizedFlow)
        source_flow2.original = Mock()
        source_flow2.original.context = water_context

        # Create match for air
        match_air_context = Mock()
        match_air_context.value = "air"
        match1 = Mock(spec=Match)
        match1.source = Mock()
        match1.source.context = match_air_context

        flowmap = Flowmap(
            source_flows=[source_flow1, source_flow2],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1]

        result = flowmap.matched_source_statistics()

        # Should be sorted by percent ascending
        assert result.iloc[0]["percent"] <= result.iloc[1]["percent"]


class TestFlowmapMatchedTargetStatistics:
    """Test Flowmap matched_target_statistics property."""

    def test_matched_target_statistics_creates_dataframe(self):
        """Test that matched_target_statistics returns a DataFrame."""
        # Create flows with contexts
        air_context = Mock()
        air_context.value = "air"
        water_context = Mock()
        water_context.value = "water"

        target_flow1 = Mock(spec=NormalizedFlow)
        target_flow1.original = Mock()
        target_flow1.original.context = air_context
        target_flow2 = Mock(spec=NormalizedFlow)
        target_flow2.original = Mock()
        target_flow2.original.context = water_context

        # Create matches
        match_air_context = Mock()
        match_air_context.value = "air"
        match1 = Mock(spec=Match)
        match1.target = Mock()
        match1.target.context = match_air_context

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[target_flow1, target_flow2],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1]

        result = flowmap.matched_target_statistics

        assert isinstance(result, pd.DataFrame)
        assert "context" in result.columns
        assert "matched" in result.columns
        assert "total" in result.columns
        assert "percent" in result.columns

    def test_matched_target_statistics_calculates_percentages(self):
        """Test that matched_target_statistics calculates correct percentages."""
        # Create flows with contexts
        air_context = Mock()
        air_context.value = "air"
        water_context = Mock()
        water_context.value = "water"

        target_flow1 = Mock(spec=NormalizedFlow)
        target_flow1.original = Mock()
        target_flow1.original.context = air_context
        target_flow2 = Mock(spec=NormalizedFlow)
        target_flow2.original = Mock()
        target_flow2.original.context = air_context
        target_flow3 = Mock(spec=NormalizedFlow)
        target_flow3.original = Mock()
        target_flow3.original.context = water_context

        # Create match
        match_air_context = Mock()
        match_air_context.value = "air"
        match1 = Mock(spec=Match)
        match1.target = Mock()
        match1.target.context = match_air_context

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[target_flow1, target_flow2, target_flow3],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1]

        result = flowmap.matched_target_statistics

        # Check air context: 1 matched, 2 total
        air_row = result[result["context"] == "air"].iloc[0]
        assert air_row["matched"] == 1
        assert air_row["total"] == 2
        assert air_row["percent"] == 0.5


class TestFlowmapPrintStatistics:
    """Test Flowmap print_statistics method."""

    @patch("builtins.print")
    def test_print_statistics_outputs_summary(self, mock_print):
        """Test that print_statistics outputs correct summary."""
        source_flow = Mock(spec=NormalizedFlow)
        target_flow = Mock(spec=NormalizedFlow)

        source_flow_for_match = Mock(spec=Flow)
        source_flow_for_match._id = 1
        target_flow_for_match = Mock(spec=Flow)
        target_flow_for_match._id = 2

        match = Mock(spec=Match)
        match.source = source_flow_for_match
        match.target = target_flow_for_match

        flowmap = Flowmap(
            source_flows=[source_flow],
            target_flows=[target_flow],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        flowmap.print_statistics()

        # Verify print was called
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]

        assert "1 source" in output
        assert "1 target" in output
        assert "1 mappings" in output
        assert "cardinalities" in output.lower()

    @patch("builtins.print")
    def test_print_statistics_handles_zero_division(self, mock_print):
        """Test that print_statistics handles zero source flows."""
        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        # Should not raise ZeroDivisionError
        flowmap.print_statistics()
        mock_print.assert_called_once()


class TestFlowmapCardinalities:
    """Test Flowmap cardinalities method."""

    def test_cardinalities_1_to_1(self):
        """Test cardinalities for 1:1 relationships."""
        source_flow = Mock(spec=Flow)
        source_flow._id = 1
        target_flow = Mock(spec=Flow)
        target_flow._id = 2

        match = Mock(spec=Match)
        match.source = source_flow
        match.target = target_flow

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.cardinalities()

        assert len(result) == 1
        assert result[0]["from"] == 1
        assert result[0]["to"] == 2
        assert result[0]["cardinality"] == "1:1"

    def test_cardinalities_1_to_n(self):
        """Test cardinalities for 1:N relationships."""
        source_flow = Mock(spec=Flow)
        source_flow._id = 1
        target_flow1 = Mock(spec=Flow)
        target_flow1._id = 2
        target_flow2 = Mock(spec=Flow)
        target_flow2._id = 3

        match1 = Mock(spec=Match)
        match1.source = source_flow
        match1.target = target_flow1
        match2 = Mock(spec=Match)
        match2.source = source_flow
        match2.target = target_flow2

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        result = flowmap.cardinalities()

        assert len(result) == 2
        assert all(r["cardinality"] == "1:N" for r in result)

    def test_cardinalities_n_to_1(self):
        """Test cardinalities for N:1 relationships."""
        source_flow1 = Mock(spec=Flow)
        source_flow1._id = 1
        source_flow2 = Mock(spec=Flow)
        source_flow2._id = 2
        target_flow = Mock(spec=Flow)
        target_flow._id = 3

        match1 = Mock(spec=Match)
        match1.source = source_flow1
        match1.target = target_flow
        match2 = Mock(spec=Match)
        match2.source = source_flow2
        match2.target = target_flow

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        result = flowmap.cardinalities()

        assert len(result) == 2
        assert all(r["cardinality"] == "N:1" for r in result)

    def test_cardinalities_n_to_m(self):
        """Test cardinalities for N:M relationships."""
        source_flow1 = Mock(spec=Flow)
        source_flow1._id = 1
        source_flow2 = Mock(spec=Flow)
        source_flow2._id = 2
        target_flow1 = Mock(spec=Flow)
        target_flow1._id = 3
        target_flow2 = Mock(spec=Flow)
        target_flow2._id = 4

        match1 = Mock(spec=Match)
        match1.source = source_flow1
        match1.target = target_flow1
        match2 = Mock(spec=Match)
        match2.source = source_flow1
        match2.target = target_flow2
        match3 = Mock(spec=Match)
        match3.source = source_flow2
        match3.target = target_flow1
        match4 = Mock(spec=Match)
        match4.source = source_flow2
        match4.target = target_flow2

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2, match3, match4]

        result = flowmap.cardinalities()

        assert len(result) == 4
        assert all(r["cardinality"] == "N:M" for r in result)

    def test_cardinalities_sorted_by_from(self):
        """Test that cardinalities are sorted by source ID."""
        matches = []
        for i in range(5, 0, -1):  # Reverse order
            source_flow = Mock(spec=Flow)
            source_flow._id = i
            target_flow = Mock(spec=Flow)
            target_flow._id = i + 10
            match = Mock(spec=Match)
            match.source = source_flow
            match.target = target_flow
            matches.append(match)

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = matches

        result = flowmap.cardinalities()

        # Verify sorted by 'from' (source ID)
        from_ids = [r["from"] for r in result]
        assert from_ids == sorted(from_ids)


class TestFlowmapToRandonneur:
    """Test Flowmap to_randonneur method."""

    @patch("flowmapper.flowmap.randonneur.Datapackage")
    def test_to_randonneur_creates_datapackage(self, mock_datapackage_class):
        """Test that to_randonneur creates a Datapackage."""
        mock_dp = Mock()
        mock_datapackage_class.return_value = mock_dp

        match = Mock(spec=Match)
        match.export.return_value = {"source": "test"}

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.to_randonneur(
            source_id="source",
            target_id="target",
            contributors=[],
            mapping_source={},
            mapping_target={},
        )

        # Verify Datapackage was created
        mock_datapackage_class.assert_called_once()
        assert result == mock_dp

    @patch("flowmapper.flowmap.randonneur.Datapackage")
    def test_to_randonneur_adds_match_data(self, mock_datapackage_class):
        """Test that to_randonneur adds match data to datapackage."""
        mock_dp = Mock()
        mock_datapackage_class.return_value = mock_dp

        match1 = Mock(spec=Match)
        match1.export.return_value = {"source": "test1"}
        match2 = Mock(spec=Match)
        match2.export.return_value = {"source": "test2"}

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match1, match2]

        flowmap.to_randonneur(
            source_id="source",
            target_id="target",
            contributors=[],
            mapping_source={},
            mapping_target={},
        )

        # Verify add_data was called with exported matches
        mock_dp.add_data.assert_called_once()
        call_args = mock_dp.add_data.call_args
        assert call_args.kwargs["verb"] == "update"
        assert len(call_args.kwargs["data"]) == 2

    @patch("flowmapper.flowmap.randonneur.Datapackage")
    def test_to_randonneur_saves_to_path(self, mock_datapackage_class):
        """Test that to_randonneur saves to path if provided."""
        mock_dp = Mock()
        mock_datapackage_class.return_value = mock_dp

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        test_path = Path("/tmp/test.json")

        flowmap.to_randonneur(
            source_id="source",
            target_id="target",
            contributors=[],
            mapping_source={},
            mapping_target={},
            path=test_path,
        )

        # Verify to_json was called
        mock_dp.to_json.assert_called_once_with(test_path)

    @patch("flowmapper.flowmap.randonneur.Datapackage")
    def test_to_randonneur_uses_custom_name(self, mock_datapackage_class):
        """Test that to_randonneur uses custom name if provided."""
        mock_dp = Mock()
        mock_datapackage_class.return_value = mock_dp

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        flowmap.to_randonneur(
            source_id="source",
            target_id="target",
            contributors=[],
            mapping_source={},
            mapping_target={},
            name="custom-name",
        )

        # Verify name was used
        call_args = mock_datapackage_class.call_args
        assert call_args.kwargs["name"] == "custom-name"

    @patch("flowmapper.flowmap.randonneur.Datapackage")
    def test_to_randonneur_defaults_name(self, mock_datapackage_class):
        """Test that to_randonneur defaults name to source-target."""
        mock_dp = Mock()
        mock_datapackage_class.return_value = mock_dp

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        flowmap.to_randonneur(
            source_id="source-v1",
            target_id="target-v2",
            contributors=[],
            mapping_source={},
            mapping_target={},
        )

        # Verify default name was used
        call_args = mock_datapackage_class.call_args
        assert call_args.kwargs["name"] == "source-v1-target-v2"


class TestFlowmapToGlad:
    """Test Flowmap to_glad method."""

    def test_to_glad_creates_dataframe(self):
        """Test that to_glad returns a DataFrame."""
        # Create match with all required attributes
        source_name = Mock()
        source_name.__str__ = Mock(return_value="Source Flow")
        source_context = Mock()
        source_context.export_as_string.return_value = "air"
        source_unit = Mock()
        source_unit.__str__ = Mock(return_value="kg")

        source_flow = Mock(spec=Flow)
        source_flow.name = source_name
        source_flow.identifier = "source-uuid"
        source_flow.context = source_context
        source_flow.unit = source_unit

        target_name = Mock()
        target_name.__str__ = Mock(return_value="Target Flow")
        target_context = Mock()
        target_context.export_as_string.return_value = "air"
        target_unit = Mock()
        target_unit.__str__ = Mock(return_value="kg")

        target_flow = Mock(spec=Flow)
        target_flow.name = target_name
        target_flow.identifier = "target-uuid"
        target_flow.context = target_context
        target_flow.unit = target_unit

        match_condition = Mock()
        match_condition.as_glad.return_value = "exact"

        match = Mock(spec=Match)
        match.source = source_flow
        match.target = target_flow
        match.condition = match_condition
        match.conversion_factor = 1.0
        match.comment = "Test match"

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.to_glad()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["SourceFlowName"] == "Source Flow"
        assert result.iloc[0]["TargetFlowName"] == "Target Flow"

    def test_to_glad_includes_all_columns(self):
        """Test that to_glad includes all required GLAD columns."""
        source_name = Mock()
        source_name.__str__ = Mock(return_value="Source")
        source_context = Mock()
        source_context.export_as_string.return_value = "air"
        source_unit = Mock()
        source_unit.__str__ = Mock(return_value="kg")

        source_flow = Mock(spec=Flow)
        source_flow.name = source_name
        source_flow.identifier = "source-id"
        source_flow.context = source_context
        source_flow.unit = source_unit

        target_name = Mock()
        target_name.__str__ = Mock(return_value="Target")
        target_context = Mock()
        target_context.export_as_string.return_value = "air"
        target_unit = Mock()
        target_unit.__str__ = Mock(return_value="kg")

        target_flow = Mock(spec=Flow)
        target_flow.name = target_name
        target_flow.identifier = "target-id"
        target_flow.context = target_context
        target_flow.unit = target_unit

        match_condition = Mock()
        match_condition.as_glad.return_value = "exact"

        match = Mock(spec=Match)
        match.source = source_flow
        match.target = target_flow
        match.condition = match_condition
        match.conversion_factor = 1.0
        match.comment = "Comment"

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.to_glad()

        expected_columns = [
            "SourceFlowName",
            "SourceFlowUUID",
            "SourceFlowContext",
            "SourceUnit",
            "MatchCondition",
            "ConversionFactor",
            "TargetFlowName",
            "TargetFlowUUID",
            "TargetFlowContext",
            "TargetUnit",
            "MemoMapper",
        ]
        assert all(col in result.columns for col in expected_columns)

    def test_to_glad_ensure_id_replaces_none_with_empty_string(self):
        """Test that to_glad replaces None identifiers with empty string when ensure_id=True."""
        source_name = Mock()
        source_name.__str__ = Mock(return_value="Source")
        source_context = Mock()
        source_context.export_as_string.return_value = "air"
        source_unit = Mock()
        source_unit.__str__ = Mock(return_value="kg")

        source_flow = Mock(spec=Flow)
        source_flow.name = source_name
        source_flow.identifier = None
        source_flow.context = source_context
        source_flow.unit = source_unit

        target_name = Mock()
        target_name.__str__ = Mock(return_value="Target")
        target_context = Mock()
        target_context.export_as_string.return_value = "air"
        target_unit = Mock()
        target_unit.__str__ = Mock(return_value="kg")

        target_flow = Mock(spec=Flow)
        target_flow.name = target_name
        target_flow.identifier = None
        target_flow.context = target_context
        target_flow.unit = target_unit

        match_condition = Mock()
        match_condition.as_glad.return_value = "exact"

        match = Mock(spec=Match)
        match.source = source_flow
        match.target = target_flow
        match.condition = match_condition
        match.conversion_factor = 1.0
        match.comment = "Comment"

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.to_glad(ensure_id=True)

        assert result.iloc[0]["SourceFlowUUID"] == ""
        assert result.iloc[0]["TargetFlowUUID"] == ""

    def test_to_glad_ensure_id_false_keeps_none(self):
        """Test that to_glad keeps None identifiers when ensure_id=False."""
        source_name = Mock()
        source_name.__str__ = Mock(return_value="Source")
        source_context = Mock()
        source_context.export_as_string.return_value = "air"
        source_unit = Mock()
        source_unit.__str__ = Mock(return_value="kg")

        source_flow = Mock(spec=Flow)
        source_flow.name = source_name
        source_flow.identifier = None
        source_flow.context = source_context
        source_flow.unit = source_unit

        target_name = Mock()
        target_name.__str__ = Mock(return_value="Target")
        target_context = Mock()
        target_context.export_as_string.return_value = "air"
        target_unit = Mock()
        target_unit.__str__ = Mock(return_value="kg")

        target_flow = Mock(spec=Flow)
        target_flow.name = target_name
        target_flow.identifier = None
        target_flow.context = target_context
        target_flow.unit = target_unit

        match_condition = Mock()
        match_condition.as_glad.return_value = "exact"

        match = Mock(spec=Match)
        match.source = source_flow
        match.target = target_flow
        match.condition = match_condition
        match.conversion_factor = 1.0
        match.comment = "Comment"

        flowmap = Flowmap(
            source_flows=[],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = [match]

        result = flowmap.to_glad(ensure_id=False)

        assert pd.isna(result.iloc[0]["SourceFlowUUID"])
        assert pd.isna(result.iloc[0]["TargetFlowUUID"])

    def test_to_glad_missing_source_includes_unmatched(self):
        """Test that to_glad includes unmatched source flows when missing_source=True."""
        # Create unmatched source flow
        unmatched_name = Mock()
        unmatched_name.__str__ = Mock(return_value="Unmatched")
        unmatched_context = Mock()
        unmatched_context.export_as_string.return_value = "air"
        unmatched_unit = Mock()
        unmatched_unit.__str__ = Mock(return_value="kg")

        unmatched_original = Mock(spec=Flow)
        unmatched_original.name = unmatched_name
        unmatched_original.identifier = "unmatched-id"
        unmatched_original.context = unmatched_context
        unmatched_original.unit = unmatched_unit

        unmatched_flow = Mock(spec=NormalizedFlow)
        unmatched_flow.matched = False
        unmatched_flow.original = unmatched_original

        flowmap = Flowmap(
            source_flows=[unmatched_flow],
            target_flows=[],
            data_preparation_functions=[],
        )
        flowmap.matches = []

        result = flowmap.to_glad(missing_source=True)

        assert len(result) == 1
        assert result.iloc[0]["SourceFlowName"] == "Unmatched"
        # Unmatched flows only have source columns, target columns will be NaN
        # The DataFrame will have all columns but target values will be NaN
        if "TargetFlowName" in result.columns:
            assert pd.isna(result.iloc[0]["TargetFlowName"])

    @patch("flowmapper.flowmap.Path")
    def test_to_glad_saves_to_excel(self, mock_path_class):
        """Test that to_glad saves to Excel when path is provided."""
        import os
        import tempfile
        from pathlib import Path as RealPath

        # Use a temporary file that we can actually create
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            test_path = RealPath(tmp.name)

        try:
            mock_path_class.return_value = test_path

            source_name = Mock()
            source_name.__str__ = Mock(return_value="Source")
            source_context = Mock()
            source_context.export_as_string.return_value = "air"
            source_unit = Mock()
            source_unit.__str__ = Mock(return_value="kg")

            source_flow = Mock(spec=Flow)
            source_flow.name = source_name
            source_flow.identifier = "source-id"
            source_flow.context = source_context
            source_flow.unit = source_unit

            target_name = Mock()
            target_name.__str__ = Mock(return_value="Target")
            target_context = Mock()
            target_context.export_as_string.return_value = "air"
            target_unit = Mock()
            target_unit.__str__ = Mock(return_value="kg")

            target_flow = Mock(spec=Flow)
            target_flow.name = target_name
            target_flow.identifier = "target-id"
            target_flow.context = target_context
            target_flow.unit = target_unit

            match_condition = Mock()
            match_condition.as_glad.return_value = "exact"

            match = Mock(spec=Match)
            match.source = source_flow
            match.target = target_flow
            match.condition = match_condition
            match.conversion_factor = 1.0
            match.comment = "Comment"

            flowmap = Flowmap(
                source_flows=[],
                target_flows=[],
                data_preparation_functions=[],
            )
            flowmap.matches = [match]

            result = flowmap.to_glad(path=test_path)

            # Verify path was converted to Path
            mock_path_class.assert_called_once_with(test_path)

            # Verify file was created
            assert test_path.exists()
        finally:
            # Clean up
            if test_path.exists():
                os.unlink(test_path)
