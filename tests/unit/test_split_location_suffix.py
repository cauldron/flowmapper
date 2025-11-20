"""Unit tests for split_location_suffix and replace_location_suffix functions."""

import pytest

from flowmapper.fields import replace_location_suffix, split_location_suffix


class TestSplitLocationSuffix:
    """Test split_location_suffix function."""

    def test_simple_location_code(self):
        """Test split_location_suffix with simple location code."""
        name, location = split_location_suffix("Ammonia, NL")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

    def test_location_code_with_extra_whitespace(self):
        """Test split_location_suffix with extra whitespace."""
        name, location = split_location_suffix("Ammonia,  \tNL")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

    def test_complicated_location_code(self):
        """Test split_location_suffix with complicated location code."""
        name, location = split_location_suffix("Ammonia, RER w/o DE+NL+NO")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert (
            location == "RER w/o DE+NL+NO"
        ), f"Expected location to be 'RER w/o DE+NL+NO', but got {location!r}"

    def test_no_location_code(self):
        """Test split_location_suffix with no location code."""
        name, location = split_location_suffix("Ammonia")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_location_code_with_dash(self):
        """Test split_location_suffix with location code using dash (should not match)."""
        name, location = split_location_suffix("Ammonia-NL")
        assert (
            name == "Ammonia-NL"
        ), f"Expected name to be 'Ammonia-NL', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_location_code_case_insensitive_fails(self):
        """Test split_location_suffix is case-insensitive for location codes."""
        name, location = split_location_suffix("Ammonia, nl")
        assert (
            name == "Ammonia, nl"
        ), f"Expected name to be 'Ammonia, nl', but got {name!r}"
        assert location is None, f"Expected location to be 'None', but got {location!r}"

    def test_multiple_commas(self):
        """Test split_location_suffix with multiple commas."""
        name, location = split_location_suffix("Ammonia, pure, NL")
        # Should match the last comma followed by location code
        assert (
            name == "Ammonia, pure"
        ), f"Expected name to be 'Ammonia, pure', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

    def test_location_code_in_middle(self):
        """Test split_location_suffix with location code not at end."""
        name, location = split_location_suffix("Ammonia, NL, pure")
        # Should not match because location code is not at the end
        assert (
            name == "Ammonia, NL, pure"
        ), f"Expected name to be 'Ammonia, NL, pure', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_empty_string(self):
        """Test split_location_suffix with empty string."""
        name, location = split_location_suffix("")
        assert name == "", f"Expected name to be '', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_only_location_code(self):
        """Test split_location_suffix with only location code."""
        name, location = split_location_suffix(", NL")
        assert name == "", f"Expected name to be '', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

    def test_whitespace_before_comma(self):
        """Test split_location_suffix with whitespace before comma."""
        name, location = split_location_suffix("Ammonia , NL")
        # The regex requires comma immediately, so this might not match
        # Testing actual behavior
        assert (
            name == "Ammonia , NL"
        ), f"Expected name to be 'Ammonia , NL' (no match), but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_no_whitespace_after_comma(self):
        """Test split_location_suffix with no whitespace after comma."""
        name, location = split_location_suffix("Ammonia,NL")
        # The regex requires whitespace after comma
        assert (
            name == "Ammonia,NL"
        ), f"Expected name to be 'Ammonia,NL' (no match), but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_various_location_codes(self):
        """Test split_location_suffix with various location codes."""
        test_cases = [
            ("Water, DE", "Water", "DE"),
            ("Water, FR", "Water", "FR"),
            ("Water, US", "Water", "US"),
            ("Water, GLO", "Water", "GLO"),
        ]
        for input_str, expected_name, expected_location in test_cases:
            name, location = split_location_suffix(input_str)
            assert (
                name == expected_name
            ), f"Expected name to be {expected_name!r} for '{input_str}', but got {name!r}"
            assert (
                location == expected_location
            ), f"Expected location to be {expected_location!r} for '{input_str}', but got {location!r}"

    def test_complex_location_with_operators(self):
        """Test split_location_suffix with complex location codes containing operators."""
        name, location = split_location_suffix("Ammonia, RER w/o DE+NL+NO")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert (
            location == "RER w/o DE+NL+NO"
        ), f"Expected location to be 'RER w/o DE+NL+NO', but got {location!r}"

    def test_location_code_with_trailing_whitespace(self):
        """Test split_location_suffix with trailing whitespace after location."""
        name, location = split_location_suffix("Ammonia, NL ")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"


class TestReplaceLocationSuffix:
    """Test replace_location_suffix function."""

    def test_simple_location_replacement(self):
        """Test replace_location_suffix with simple location code."""
        result = replace_location_suffix("Ammonia, NL", "DE")
        assert result == "Ammonia, DE", f"Expected 'Ammonia, DE', but got {result!r}"

    def test_location_replacement_with_extra_whitespace(self):
        """Test replace_location_suffix with extra whitespace."""
        result = replace_location_suffix("Ammonia,  \tNL", "DE")
        assert (
            result == "Ammonia,  \tDE"
        ), f"Expected 'Ammonia,  \\tDE', but got {result!r}"

    def test_complicated_location_replacement(self):
        """Test replace_location_suffix with complicated location code."""
        result = replace_location_suffix("Ammonia, RER w/o DE+NL+NO", "GLO")
        assert result == "Ammonia, GLO", f"Expected 'Ammonia, GLO', but got {result!r}"

    def test_no_location_code_raises_value_error(self):
        """Test replace_location_suffix with no location code (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia", "DE")

    def test_location_code_with_dash_raises_value_error(self):
        """Test replace_location_suffix with location code using dash (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia-NL", "DE")

    def test_location_code_case_insensitive_raises_value_error(self):
        """Test replace_location_suffix with lowercase location (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia, nl", "DE")

    def test_multiple_commas_replacement(self):
        """Test replace_location_suffix with multiple commas."""
        result = replace_location_suffix("Ammonia, pure, NL", "FR")
        # Should replace the last location code
        assert (
            result == "Ammonia, pure, FR"
        ), f"Expected 'Ammonia, pure, FR', but got {result!r}"

    def test_location_code_in_middle_raises_value_error(self):
        """Test replace_location_suffix with location code not at end (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia, NL, pure", "DE")

    def test_empty_string_raises_value_error(self):
        """Test replace_location_suffix with empty string (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("", "DE")

    def test_only_location_code_replacement(self):
        """Test replace_location_suffix with only location code."""
        result = replace_location_suffix(", NL", "DE")
        assert result == ", DE", f"Expected ', DE', but got {result!r}"

    def test_whitespace_before_comma_raises_value_error(self):
        """Test replace_location_suffix with whitespace before comma (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia , NL", "DE")

    def test_no_whitespace_after_comma_raises_value_error(self):
        """Test replace_location_suffix with no whitespace after comma (should raise ValueError)."""
        with pytest.raises(ValueError, match="No location suffix found"):
            replace_location_suffix("Ammonia,NL", "DE")

    def test_various_location_codes_replacement(self):
        """Test replace_location_suffix with various location codes."""
        test_cases = [
            ("Water, DE", "FR", "Water, FR"),
            ("Water, FR", "US", "Water, US"),
            ("Water, US", "GLO", "Water, GLO"),
            ("Water, GLO", "DE", "Water, DE"),
        ]
        for input_str, new_location, expected in test_cases:
            result = replace_location_suffix(input_str, new_location)
            assert (
                result == expected
            ), f"Expected {expected!r} for '{input_str}' -> '{new_location}', but got {result!r}"

    def test_complex_location_with_operators_replacement(self):
        """Test replace_location_suffix with complex location codes containing operators."""
        result = replace_location_suffix("Ammonia, RER w/o DE+NL+NO", "GLO")
        assert result == "Ammonia, GLO", f"Expected 'Ammonia, GLO', but got {result!r}"

    def test_location_code_with_trailing_whitespace_replacement(self):
        """Test replace_location_suffix with trailing whitespace after location."""
        result = replace_location_suffix("Ammonia, NL ", "DE")
        assert (
            result == "Ammonia, DE "
        ), f"Expected 'Ammonia, DE ' (preserving trailing space), but got {result!r}"

    def test_replace_with_empty_string(self):
        """Test replace_location_suffix replacing location with empty string."""
        result = replace_location_suffix("Ammonia, NL", "")
        assert (
            result == "Ammonia, "
        ), f"Expected 'Ammonia, ' (empty location), but got {result!r}"

    def test_replace_with_longer_location(self):
        """Test replace_location_suffix replacing with a longer location code."""
        result = replace_location_suffix("Ammonia, NL", "RER w/o DE+NL+NO")
        assert (
            result == "Ammonia, RER w/o DE+NL+NO"
        ), f"Expected 'Ammonia, RER w/o DE+NL+NO', but got {result!r}"

    def test_replace_with_shorter_location(self):
        """Test replace_location_suffix replacing with a shorter location code."""
        result = replace_location_suffix("Ammonia, RER w/o DE+NL+NO", "NL")
        assert result == "Ammonia, NL", f"Expected 'Ammonia, NL', but got {result!r}"
