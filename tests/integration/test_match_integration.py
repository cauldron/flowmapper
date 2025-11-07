"""Integration tests for match.py functions using real Flow objects."""

import pytest

from flowmapper.flow import Flow
from flowmapper.match import (
    match_biogenic_to_non_fossil,
    match_custom_names_with_location_codes,
    match_emissions_with_suffix_ion,
    match_flows_with_suffix_unspecified_origin,
    match_names_with_location_codes,
    match_names_with_roman_numerals_in_parentheses,
    match_non_ionic_state,
    match_resource_names_with_location_codes_and_parent_context,
    match_resources_with_suffix_in_air,
    match_resources_with_suffix_in_ground,
    match_resources_with_suffix_in_water,
    match_resources_with_wrong_subcontext,
    match_rules,
)


class TestMatchNamesWithRomanNumeralsInParentheses:
    """Integration tests for match_names_with_roman_numerals_in_parentheses."""

    def test_match_names_with_roman_numerals_in_parentheses_matching(self, transformations):
        """Test matching names with roman numerals in parentheses."""
        source = {
            "name": "Iron (ii)",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Iron ii",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_names_with_roman_numerals_in_parentheses(s, t, [], [])

        assert result == {"comment": "With/without roman numerals in parentheses"}

    def test_match_names_with_roman_numerals_in_parentheses_uppercase(self, transformations):
        """Test matching names with uppercase roman numerals in parentheses."""
        source = {
            "name": "Iron (II)",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Iron II",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_names_with_roman_numerals_in_parentheses(s, t, [], [])

        assert result == {"comment": "With/without roman numerals in parentheses"}

    def test_match_names_with_roman_numerals_in_parentheses_mixed_case(self, transformations):
        """Test matching names with mixed case roman numerals in parentheses."""
        source = {
            "name": "Iron (II)",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Iron ii",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_names_with_roman_numerals_in_parentheses(s, t, [], [])

        assert result == {"comment": "With/without roman numerals in parentheses"}

    def test_match_names_with_roman_numerals_in_parentheses_no_match(self, transformations):
        """Test when names don't match even after removing roman numerals."""
        source = {
            "name": "Iron (II)",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Copper",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_names_with_roman_numerals_in_parentheses(s, t, [], [])

        assert result is None

    def test_match_names_with_roman_numerals_in_parentheses_different_context(self, transformations):
        """Test when contexts are different."""
        source = {
            "name": "Iron (II)",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Iron",
            "context": ["ground"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_names_with_roman_numerals_in_parentheses(s, t, [], [])

        assert result is None


class TestMatchResourceNamesWithLocationCodesAndParentContext:
    """Integration tests for match_resource_names_with_location_codes_and_parent_context."""

    def test_match_resource_names_with_location_codes_and_parent_context_matching(self, transformations):
        """Test matching resource names with location codes and parent context."""
        source = {
            "name": "Water, NL",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }
        target = {
            "name": "Water",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resource_names_with_location_codes_and_parent_context(s, t, [], [])

        assert result is not None
        assert result["comment"] == "Name matching with location code and parent context"
        assert result["location"] == "NL"

    def test_match_resource_names_with_location_codes_water_conversion(self, transformations):
        """Test water conversion factor for resource names with location codes."""
        source = {
            "name": "Water, NL",
            "context": ["natural resource", "in air"],
            "unit": "cubic_meter",
        }
        target = {
            "name": "Water",
            "context": ["natural resource", "in air"],
            "unit": "kilogram",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resource_names_with_location_codes_and_parent_context(s, t, [], [])

        assert result is not None
        assert result["conversion_factor"] == 1000.0

    def test_match_resource_names_with_location_codes_no_match(self, transformations):
        """Test when resource names don't match."""
        source = {
            "name": "Water, NL",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }
        target = {
            "name": "Air",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resource_names_with_location_codes_and_parent_context(s, t, [], [])

        assert result is None


class TestMatchResourcesWithSuffixInGround:
    """Integration tests for match_resources_with_suffix_in_ground."""

    def test_match_resources_with_suffix_in_ground_matching(self, transformations):
        """Test matching resources with suffix 'in ground'."""
        source = {
            "name": "Copper",
            "context": ["natural resource", "in ground"],
            "unit": "kg",
        }
        target = {
            "name": "Copper, in ground",
            "context": ["natural resource", "in ground"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_ground(s, t, [], [])

        assert result == {"comment": "Resources with suffix in ground"}

    def test_match_resources_with_suffix_in_ground_no_match(self, transformations):
        """Test when resources don't match."""
        source = {
            "name": "Copper",
            "context": ["natural resource", "in ground"],
            "unit": "kg",
        }
        target = {
            "name": "Iron, in ground",
            "context": ["natural resource", "in ground"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_ground(s, t, [], [])

        assert result is None


class TestMatchFlowsWithSuffixUnspecifiedOrigin:
    """Integration tests for match_flows_with_suffix_unspecified_origin."""

    def test_match_flows_with_suffix_unspecified_origin_matching(self, transformations):
        """Test matching flows with suffix 'unspecified origin'."""
        source = {
            "name": "Carbon dioxide",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Carbon dioxide, unspecified origin",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_flows_with_suffix_unspecified_origin(s, t, [], [])

        assert result == {"comment": "Flows with suffix unspecified origin"}

    def test_match_flows_with_suffix_unspecified_origin_no_match(self, transformations):
        """Test when flows don't match."""
        source = {
            "name": "Carbon dioxide",
            "context": ["air"],
            "unit": "kg",
        }
        target = {
            "name": "Methane, unspecified origin",
            "context": ["air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_flows_with_suffix_unspecified_origin(s, t, [], [])

        assert result is None


class TestMatchResourcesWithSuffixInWater:
    """Integration tests for match_resources_with_suffix_in_water."""

    def test_match_resources_with_suffix_in_water_matching(self, transformations):
        """Test matching resources with suffix 'in water'."""
        source = {
            "name": "Copper",
            "context": ["natural resource", "in water"],
            "unit": "kg",
        }
        target = {
            "name": "Copper, in water",
            "context": ["natural resource", "in water"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_water(s, t, [], [])

        assert result == {"comment": "Resources with suffix in water"}

    def test_match_resources_with_suffix_in_water_no_match(self, transformations):
        """Test when resources don't match."""
        source = {
            "name": "Copper",
            "context": ["natural resource", "in water"],
            "unit": "kg",
        }
        target = {
            "name": "Iron, in water",
            "context": ["natural resource", "in water"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_water(s, t, [], [])

        assert result is None


class TestMatchResourcesWithSuffixInAir:
    """Integration tests for match_resources_with_suffix_in_air."""

    def test_match_resources_with_suffix_in_air_matching(self, transformations):
        """Test matching resources with suffix 'in air'."""
        source = {
            "name": "Nitrogen",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }
        target = {
            "name": "Nitrogen, in air",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_air(s, t, [], [])

        assert result == {"comment": "Resources with suffix in air"}

    def test_match_resources_with_suffix_in_air_no_match(self, transformations):
        """Test when resources don't match."""
        source = {
            "name": "Nitrogen",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }
        target = {
            "name": "Oxygen, in air",
            "context": ["natural resource", "in air"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_resources_with_suffix_in_air(s, t, [], [])

        assert result is None


class TestMatchEmissionsWithSuffixIon:
    """Integration tests for match_emissions_with_suffix_ion."""

    def test_match_emissions_with_suffix_ion_matching(self, transformations):
        """Test matching emissions with suffix 'ion'."""
        source = {
            "name": "Copper",
            "context": ["emission", "to water"],
            "unit": "kg",
        }
        target = {
            "name": "Copper, ion",
            "context": ["emission", "to water"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_emissions_with_suffix_ion(s, t, [], [])

        assert result == {"comment": "Match emissions with suffix ion"}

    def test_match_emissions_with_suffix_ion_no_match(self, transformations):
        """Test when emissions don't match."""
        source = {
            "name": "Copper",
            "context": ["emission", "to water"],
            "unit": "kg",
        }
        target = {
            "name": "Iron, ion",
            "context": ["emission", "to water"],
            "unit": "kg",
        }

        s = Flow(source, transformations)
        t = Flow(target, transformations)

        result = match_emissions_with_suffix_ion(s, t, [], [])

        assert result is None, f"Expected result to be None, but got {result}"


class TestMatchRules:
    """Integration tests for match_rules function."""

    def test_match_rules_returns_list(self):
        """Test that match_rules returns a list of functions."""
        rules = match_rules()

        assert isinstance(rules, list)
        assert len(rules) > 0
        assert all(callable(rule) for rule in rules)

    def test_match_rules_contains_expected_functions(self):
        """Test that match_rules contains expected matching functions."""
        from flowmapper.match import (
            match_biogenic_to_non_fossil,
            match_custom_names_with_location_codes,
            match_emissions_with_suffix_ion,
            match_flows_with_suffix_unspecified_origin,
            match_identical_cas_numbers,
            match_identical_identifier,
            match_identical_names,
            match_identical_names_in_preferred_synonyms,
            match_identical_names_in_synonyms,
            match_identical_names_without_commas,
            match_names_with_location_codes,
            match_names_with_roman_numerals_in_parentheses,
            match_non_ionic_state,
            match_resource_names_with_location_codes_and_parent_context,
            match_resources_with_suffix_in_air,
            match_resources_with_suffix_in_ground,
            match_resources_with_suffix_in_water,
            match_resources_with_wrong_subcontext,
        )

        rules = match_rules()

        assert match_identical_identifier in rules
        assert match_identical_names in rules
        assert match_identical_names_without_commas in rules
        assert match_resources_with_suffix_in_ground in rules
        assert match_resources_with_suffix_in_water in rules
        assert match_resources_with_suffix_in_air in rules
        assert match_flows_with_suffix_unspecified_origin in rules
        assert match_resources_with_wrong_subcontext in rules
        assert match_emissions_with_suffix_ion in rules
        assert match_names_with_roman_numerals_in_parentheses in rules
        assert match_names_with_location_codes in rules
        assert match_resource_names_with_location_codes_and_parent_context in rules
        assert match_custom_names_with_location_codes in rules
        assert match_identical_cas_numbers in rules
        assert match_non_ionic_state in rules
        assert match_biogenic_to_non_fossil in rules
        assert match_identical_names_in_preferred_synonyms in rules
        assert match_identical_names_in_synonyms in rules

    def test_match_rules_order(self):
        """Test that match_rules returns functions in expected order."""
        rules = match_rules()

        # Check that some key functions are in the expected order
        rule_names = [rule.__name__ for rule in rules]

        # match_identical_identifier should be first
        assert rule_names[0] == "match_identical_identifier", f"Expected rule_names[0] to be 'match_identical_identifier', but got {rule_names[0]!r}"

        # match_identical_names should be early
        assert "match_identical_names" in rule_names[:5], f"Expected 'match_identical_names' to be in rule_names[:5], but got {rule_names[:5]}"

        # More complex matches should be later
        assert "match_custom_names_with_location_codes" in rule_names, f"Expected 'match_custom_names_with_location_codes' to be in rule_names, but it was not"
        assert "match_biogenic_to_non_fossil" in rule_names[-5:], f"Expected 'match_biogenic_to_non_fossil' to be in rule_names[-5:], but got {rule_names[-5:]}"

