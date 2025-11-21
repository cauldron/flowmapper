"""Unit tests for equivalent_names function."""

import pytest

from flowmapper.matching.specialized import equivalent_names


class TestEquivalentNames:
    """Test equivalent_names function."""

    def test_equivalent_with_in_ground_suffix(self):
        """Test that names with ', in ground' suffix are equivalent."""
        assert equivalent_names("Carbon dioxide, in ground", "Carbon dioxide") is True
        assert equivalent_names("Carbon dioxide", "Carbon dioxide, in ground") is True

    def test_equivalent_with_ion_suffix(self):
        """Test that names with ', ion' suffix are equivalent."""
        assert equivalent_names("Carbon dioxide, ion", "Carbon dioxide") is True
        assert equivalent_names("Carbon dioxide", "Carbon dioxide, ion") is True

    def test_equivalent_with_in_air_suffix(self):
        """Test that names with ', in air' suffix are equivalent."""
        assert equivalent_names("Carbon dioxide, in air", "Carbon dioxide") is True
        assert equivalent_names("Carbon dioxide", "Carbon dioxide, in air") is True

    def test_equivalent_with_in_water_suffix(self):
        """Test that names with ', in water' suffix are equivalent."""
        assert equivalent_names("Carbon dioxide, in water", "Carbon dioxide") is True
        assert equivalent_names("Carbon dioxide", "Carbon dioxide, in water") is True

    def test_equivalent_with_unspecified_origin_suffix(self):
        """Test that names with ', unspecified origin' suffix are equivalent."""
        assert (
            equivalent_names("Carbon dioxide, unspecified origin", "Carbon dioxide")
            is True
        )
        assert (
            equivalent_names("Carbon dioxide", "Carbon dioxide, unspecified origin")
            is True
        )

    def test_not_equivalent_different_suffixes(self):
        """Test that names with different suffixes are not equivalent."""
        assert (
            equivalent_names("Carbon dioxide, in ground", "Carbon dioxide, in air")
            is False
        )
        assert (
            equivalent_names("Carbon dioxide, in air", "Carbon dioxide, in water")
            is False
        )

    def test_equivalent_biogenic_and_non_fossil(self):
        """Test that biogenic and non-fossil names are equivalent."""
        assert equivalent_names("Methane, biogenic", "Methane, non-fossil") is True
        assert equivalent_names("Methane, non-fossil", "Methane, biogenic") is True

    def test_biogenic_non_fossil_with_matching_base(self):
        """Test biogenic/non-fossil equivalence with matching base names."""
        assert (
            equivalent_names("Carbon dioxide, biogenic", "Carbon dioxide, non-fossil")
            is True
        )
        assert equivalent_names("Water, biogenic", "Water, non-fossil") is True

    def test_biogenic_non_fossil_with_different_base(self):
        """Test that biogenic/non-fossil with different base names are not equivalent."""
        assert equivalent_names("Methane, biogenic", "Ethane, non-fossil") is False

    def test_not_equivalent_different_base_names(self):
        """Test that names with different base names are not equivalent."""
        assert equivalent_names("Carbon dioxide", "Carbon monoxide") is False
        assert equivalent_names("Methane", "Ethane") is False

    def test_not_equivalent_same_suffix_both_sides(self):
        """Test that names with same suffix on both sides are not equivalent."""
        # Both have the same suffix, so they're not equivalent (base names differ)
        assert equivalent_names("Carbon dioxide, in air", "Methane, in air") is False

    def test_case_sensitive_base_name(self):
        """Test that base name comparison is case-sensitive."""
        assert equivalent_names("Carbon dioxide, in air", "carbon dioxide") is False
        assert equivalent_names("carbon dioxide, in air", "Carbon dioxide") is False

    def test_empty_strings(self):
        """Test that empty strings are not equivalent."""
        assert equivalent_names("", "") is False
        assert equivalent_names("Carbon dioxide", "") is False
        assert equivalent_names("", "Carbon dioxide") is False

    def test_suffix_only(self):
        """Test that suffix-only strings are handled correctly."""
        # When one string is just the suffix and the other is empty,
        # removing the suffix from the first gives an empty string,
        # which matches the second empty string, so they're equivalent
        assert equivalent_names(", in air", "") is True
        assert equivalent_names("", ", in air") is True

    def test_multiple_suffixes_not_supported(self):
        """Test that names with multiple supported suffixes are not equivalent."""
        # Note: This tests the current behavior - names with multiple suffixes
        # are not handled by the function
        assert (
            equivalent_names("Carbon dioxide, in air, ion", "Carbon dioxide") is False
        )

    def test_biogenic_with_other_suffix(self):
        """Test that biogenic with other suffix is not equivalent to base."""
        # "Carbon dioxide, biogenic" should not match "Carbon dioxide, in air"
        # because biogenic is only equivalent to non-fossil
        assert (
            equivalent_names("Carbon dioxide, biogenic", "Carbon dioxide, in air")
            is False
        )

    def test_non_fossil_with_other_suffix(self):
        """Test that non-fossil with other suffix is not equivalent to base."""
        assert (
            equivalent_names("Carbon dioxide, non-fossil", "Carbon dioxide, in air")
            is False
        )
