"""Unit tests for split_location_suffix function."""

from flowmapper.location import split_location_suffix


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
        assert location == "RER w/o DE+NL+NO", f"Expected location to be 'RER w/o DE+NL+NO', but got {location!r}"

    def test_no_location_code(self):
        """Test split_location_suffix with no location code."""
        name, location = split_location_suffix("Ammonia")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_location_code_with_dash(self):
        """Test split_location_suffix with location code using dash (should not match)."""
        name, location = split_location_suffix("Ammonia-NL")
        assert name == "Ammonia-NL", f"Expected name to be 'Ammonia-NL', but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_location_code_case_insensitive_fails(self):
        """Test split_location_suffix is case-insensitive for location codes."""
        name, location = split_location_suffix("Ammonia, nl")
        assert name == "Ammonia, nl", f"Expected name to be 'Ammonia, nl', but got {name!r}"
        assert location is None, f"Expected location to be 'None', but got {location!r}"

    def test_multiple_commas(self):
        """Test split_location_suffix with multiple commas."""
        name, location = split_location_suffix("Ammonia, pure, NL")
        # Should match the last comma followed by location code
        assert name == "Ammonia, pure", f"Expected name to be 'Ammonia, pure', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

    def test_location_code_in_middle(self):
        """Test split_location_suffix with location code not at end."""
        name, location = split_location_suffix("Ammonia, NL, pure")
        # Should not match because location code is not at the end
        assert name == "Ammonia, NL, pure", f"Expected name to be 'Ammonia, NL, pure', but got {name!r}"
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
        assert name == "Ammonia , NL", f"Expected name to be 'Ammonia , NL' (no match), but got {name!r}"
        assert location is None, f"Expected location to be None, but got {location!r}"

    def test_no_whitespace_after_comma(self):
        """Test split_location_suffix with no whitespace after comma."""
        name, location = split_location_suffix("Ammonia,NL")
        # The regex requires whitespace after comma
        assert name == "Ammonia,NL", f"Expected name to be 'Ammonia,NL' (no match), but got {name!r}"
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
            assert name == expected_name, f"Expected name to be {expected_name!r} for '{input_str}', but got {name!r}"
            assert location == expected_location, f"Expected location to be {expected_location!r} for '{input_str}', but got {location!r}"

    def test_complex_location_with_operators(self):
        """Test split_location_suffix with complex location codes containing operators."""
        name, location = split_location_suffix("Ammonia, RER w/o DE+NL+NO")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location == "RER w/o DE+NL+NO", f"Expected location to be 'RER w/o DE+NL+NO', but got {location!r}"

    def test_location_code_with_trailing_whitespace(self):
        """Test split_location_suffix with trailing whitespace after location."""
        name, location = split_location_suffix("Ammonia, NL ")
        assert name == "Ammonia", f"Expected name to be 'Ammonia', but got {name!r}"
        assert location == "NL", f"Expected location to be 'NL', but got {location!r}"

