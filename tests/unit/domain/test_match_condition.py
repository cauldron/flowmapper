"""Unit tests for MatchCondition enum."""

import pytest

from flowmapper.domain.match_condition import MatchCondition


class TestMatchConditionAsGlad:
    """Test MatchCondition as_glad method."""

    def test_exact_match_returns_equals(self):
        """Test exact match returns '='."""
        assert (
            MatchCondition.exact.as_glad() == "="
        ), "Expected exact match to return '='"

    def test_close_match_returns_tilde(self):
        """Test close match returns '~'."""
        assert (
            MatchCondition.close.as_glad() == "~"
        ), "Expected close match to return '~'"

    def test_related_match_returns_tilde(self):
        """Test related match returns '~'."""
        assert (
            MatchCondition.related.as_glad() == "~"
        ), "Expected related match to return '~'"

    def test_narrow_match_returns_greater_than(self):
        """Test narrow match returns '>'."""
        assert (
            MatchCondition.narrow.as_glad() == ">"
        ), "Expected narrow match to return '>'"

    def test_broad_match_returns_less_than(self):
        """Test broad match returns '<'."""
        assert (
            MatchCondition.broad.as_glad() == "<"
        ), "Expected broad match to return '<'"

    def test_all_enum_values_have_glad_symbols(self):
        """Test all enum values have corresponding GLAD symbols."""
        glad_symbols = {condition.as_glad() for condition in MatchCondition}

        assert "=" in glad_symbols, "Expected '=' symbol for exact match"
        assert "~" in glad_symbols, "Expected '~' symbol for close/related match"
        assert ">" in glad_symbols, "Expected '>' symbol for narrow match"
        assert "<" in glad_symbols, "Expected '<' symbol for broad match"


class TestMatchConditionEnumValues:
    """Test MatchCondition enum values."""

    def test_all_values_are_valid_skos_uris(self):
        """Test all enum values are valid SKOS URIs."""
        skos_base = "http://www.w3.org/2004/02/skos/core#"

        for condition in MatchCondition:
            assert condition.value.startswith(
                skos_base
            ), f"Expected {condition.name} to be SKOS URI"
            assert "#" in condition.value, f"Expected {condition.value} to contain '#'"

    def test_enum_can_be_used_in_comparisons(self):
        """Test enum can be used in comparisons."""
        assert MatchCondition.exact == MatchCondition.exact, "Expected exact == exact"
        assert MatchCondition.exact != MatchCondition.close, "Expected exact != close"
        assert MatchCondition.exact in [
            MatchCondition.exact,
            MatchCondition.close,
        ], "Expected exact in list"

    def test_enum_string_representation(self):
        """Test enum string representation."""
        assert (
            str(MatchCondition.exact) == MatchCondition.exact.value
        ), "Expected str() to return value"
        assert (
            repr(MatchCondition.exact)
            == f"<MatchCondition.exact: '{MatchCondition.exact.value}'>"
        ), "Expected repr() to show enum name and value"
