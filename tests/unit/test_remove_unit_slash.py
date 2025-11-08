"""Unit tests for remove_unit_slash function."""

from unittest.mock import Mock, patch

from flowmapper.utils import remove_unit_slash


class TestRemoveUnitSlash:
    """Test remove_unit_slash function."""

    def test_no_match_returns_original_name(self):
        """Test that remove_unit_slash returns original name when no match is found."""
        flow = Mock()
        flow.name = "water"
        flow.unit = Mock()
        
        result = remove_unit_slash(flow)
        assert result == "water", f"Expected result to be 'water', but got {result!r}"

    def test_match_at_end_removes_slash_and_unit(self):
        """Test that remove_unit_slash removes /m3 or /kg when at end of string with whitespace."""
        # Test with /m3 at end with whitespace - unit is captured
        flow = Mock()
        flow.name = "water/m3 "
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        # match.end() == len(name), so removes from match.start() to end
        assert result == "water", f"Expected result to be 'water', but got {result!r}"
        
        # Test with /kg at end with whitespace
        flow.name = "water/kg "
        result = remove_unit_slash(flow)
        assert result == "water", f"Expected result to be 'water', but got {result!r}"

    def test_match_at_end_with_comma(self):
        """Test that remove_unit_slash skips match with only comma after unit at end."""
        flow = Mock()
        flow.name = "water/m3,"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water/m3,", f"Expected result to be 'water/m3,', but got {result!r}"

    def test_match_in_middle_replaces_with_comma_space(self):
        """Test that remove_unit_slash replaces /m3 or /kg in middle with ', '."""
        flow = Mock()
        flow.name = "water/m3, pure"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"
        
        # Test with /kg
        flow.name = "water/kg, pure"
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"

    def test_match_with_whitespace(self):
        """Test that remove_unit_slash handles whitespace after unit."""
        flow = Mock()
        flow.name = "water/m3 "
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        # match.end() == len(name) (whitespace is included in match), so removes from start to end
        assert result == "water", f"Expected result to be 'water', but got {result!r}"

    def test_match_with_comma_and_whitespace(self):
        """Test that remove_unit_slash handles comma and whitespace."""
        flow = Mock()
        flow.name = "water/m3, pure"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"

    def test_multiple_matches_skipped(self):
        """Test that remove_unit_slash only processes the first match."""
        flow = Mock()
        flow.name = "water/m3/kg"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water/m3/kg", f"Expected result to be 'water/m3/kg', but got {result!r}"

    def test_incompatible_unit_logs_warning(self):
        """Test that remove_unit_slash logs warning for incompatible units."""
        flow = Mock()
        flow.name = "water/m3 "
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=False)
        flow.__repr__ = Mock(return_value="Flow(water/m3)")
        
        # Should still return the modified name
        result = remove_unit_slash(flow)
        assert result == "water", f"Expected result to be 'water', but got {result!r}"
        # Verify compatible was called
        flow.unit.compatible.assert_called()

    @patch('flowmapper.utils.logger')
    def test_incompatible_unit_logs_warning_message(self, mock_logger):
        """Test that remove_unit_slash logs the correct warning message for incompatible units."""
        flow = Mock()
        flow.name = "water/m3 pure"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=False)
        flow.__repr__ = Mock(return_value="Flow(water/m3 pure)")
        
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"
        
        # Verify warning was called
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "has unit" in warning_call, f"Expected warning message to contain 'has unit', but got {warning_call!r}"
        assert "but name refers to incompatible unit" in warning_call, f"Expected warning message to contain 'but name refers to incompatible unit', but got {warning_call!r}"
        assert "m3" in warning_call, f"Expected warning message to contain 'm3', but got {warning_call!r}"

    @patch('flowmapper.utils.logger')
    def test_incompatible_unit_logs_warning_with_kg(self, mock_logger):
        """Test that remove_unit_slash logs warning message with kg unit."""
        flow = Mock()
        flow.name = "water/kg pure"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=False)
        flow.__repr__ = Mock(return_value="Flow(water/kg pure)")
        
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"
        
        # Verify warning was called with kg
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "kg" in warning_call, f"Expected warning message to contain 'kg', but got {warning_call!r}"

    @patch('flowmapper.utils.logger')
    def test_compatible_unit_no_warning(self, mock_logger):
        """Test that remove_unit_slash doesn't log warning for compatible units."""
        flow = Mock()
        flow.name = "water/m3 "
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water", f"Expected result to be 'water', but got {result!r}"
        # Verify compatible was called
        flow.unit.compatible.assert_called()
        # Verify warning was NOT called
        mock_logger.warning.assert_not_called()

    def test_match_when_unit_not_followed_by_whitespace_or_comma(self):
        """Test that remove_unit_slash doesn't match when unit is not followed by whitespace or comma."""
        flow = Mock()
        flow.name = "water/m3x"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        # The regex requires whitespace, comma, or end of string after /m3 or /kg
        # Since /m3x doesn't match, no change should occur
        assert result == "water/m3x", f"Expected result to be 'water/m3x' (no match), but got {result!r}"

    def test_match_not_at_end_replaces(self):
        """Test that remove_unit_slash replaces match when not at end."""
        flow = Mock()
        flow.name = "water/m3 pure"
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        assert result == "water, pure", f"Expected result to be 'water, pure', but got {result!r}"

    def test_case_sensitivity(self):
        """Test that remove_unit_slash is case-sensitive for unit pattern."""
        flow = Mock()
        flow.name = "water/M3"  # Uppercase M3
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        # Should not match uppercase M3
        result = remove_unit_slash(flow)
        assert result == "water/M3", f"Expected result to be 'water/M3' (no match), but got {result!r}"

    def test_no_unit_slash_pattern(self):
        """Test that remove_unit_slash doesn't match other slash patterns."""
        flow = Mock()
        flow.name = "water/liter"
        flow.unit = Mock()
        
        result = remove_unit_slash(flow)
        assert result == "water/liter", f"Expected result to be 'water/liter' (no match), but got {result!r}"

    def test_empty_name(self):
        """Test that remove_unit_slash handles empty name."""
        flow = Mock()
        flow.name = ""
        flow.unit = Mock()
        
        result = remove_unit_slash(flow)
        assert result == "", f"Expected result to be '', but got {result!r}"

    def test_name_with_only_unit_slash(self):
        """Test that remove_unit_slash handles name with only /m3 or /kg with whitespace."""
        flow = Mock()
        flow.name = "/m3 "
        flow.unit = Mock()
        flow.unit.compatible = Mock(return_value=True)
        
        result = remove_unit_slash(flow)
        # match.end() == len(name), so removes from match.start() to end
        assert result == "", f"Expected result to be '', but got {result!r}"
        
        # Test with /kg
        flow.name = "/kg "
        result = remove_unit_slash(flow)
        assert result == "", f"Expected result to be '', but got {result!r}"

