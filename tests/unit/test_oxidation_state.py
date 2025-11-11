"""Unit tests for OxidationState class."""

import pytest

from flowmapper.oxidation_state import OxidationState


class TestOxidationStateInitialization:
    """Test OxidationState initialization."""

    def test_init_with_positive_value(self):
        """Test initialization with positive value."""
        os = OxidationState(3)
        assert os.value == 3, f"Expected os.value to be 3, but got {os.value}"

    def test_init_with_negative_value(self):
        """Test initialization with negative value."""
        os = OxidationState(-2)
        assert os.value == -2, f"Expected os.value to be -2, but got {os.value}"

    def test_init_with_zero(self):
        """Test initialization with zero."""
        os = OxidationState(0)
        assert os.value == 0, f"Expected os.value to be 0, but got {os.value}"

    def test_init_with_boundary_values(self):
        """Test initialization with boundary values."""
        os_min = OxidationState(-5)
        os_max = OxidationState(9)
        assert (
            os_min.value == -5
        ), f"Expected os_min.value to be -5, but got {os_min.value}"
        assert (
            os_max.value == 9
        ), f"Expected os_max.value to be 9, but got {os_max.value}"


class TestOxidationStateEq:
    """Test OxidationState __eq__ method."""

    def test_eq_with_same_oxidation_state(self):
        """Test equality with same OxidationState instance."""
        os1 = OxidationState(3)
        os2 = OxidationState(3)
        assert (
            os1 == os2
        ), f"Expected os1 to equal os2, but they are not equal (os1={os1.value}, os2={os2.value})"

    def test_eq_with_different_oxidation_state(self):
        """Test equality with different OxidationState."""
        os1 = OxidationState(3)
        os2 = OxidationState(4)
        assert (
            os1 != os2
        ), f"Expected os1 to not equal os2, but they are equal (os1={os1.value}, os2={os2.value})"

    def test_eq_with_integer(self):
        """Test equality with integer."""
        os = OxidationState(3)
        assert (
            os == 3
        ), f"Expected os to equal 3, but they are not equal (os={os.value})"
        assert (
            os != 4
        ), f"Expected os to not equal 4, but they are equal (os={os.value})"

    def test_eq_with_negative_integer(self):
        """Test equality with negative integer."""
        os = OxidationState(-2)
        assert (
            os == -2
        ), f"Expected os to equal -2, but they are not equal (os={os.value})"
        assert (
            os != -3
        ), f"Expected os to not equal -3, but they are equal (os={os.value})"

    def test_eq_with_zero(self):
        """Test equality with zero."""
        os = OxidationState(0)
        assert (
            os == 0
        ), f"Expected os to equal 0, but they are not equal (os={os.value})"
        assert (
            os != 1
        ), f"Expected os to not equal 1, but they are equal (os={os.value})"


class TestOxidationStateHasOxidationState:
    """Test OxidationState has_oxidation_state static method."""

    def test_has_oxidation_state_with_roman_numeral_lowercase(self):
        """Test has_oxidation_state with lowercase roman numeral."""
        assert OxidationState.has_oxidation_state(
            "chromium (iii)"
        ), "Expected has_oxidation_state('chromium (iii)') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "iron (ii)"
        ), "Expected has_oxidation_state('iron (ii)') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "manganese (vi)"
        ), "Expected has_oxidation_state('manganese (vi)') to return True, but it returned False"

    def test_has_oxidation_state_with_roman_numeral_uppercase(self):
        """Test has_oxidation_state with uppercase roman numeral."""
        assert OxidationState.has_oxidation_state(
            "Iron (II)"
        ), "Expected has_oxidation_state('Iron (II)') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "Chromium (III)"
        ), "Expected has_oxidation_state('Chromium (III)') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "Mercury (IV)"
        ), "Expected has_oxidation_state('Mercury (IV)') to return True, but it returned False"

    def test_has_oxidation_state_with_roman_numeral_no_parentheses(self):
        """Test has_oxidation_state with roman numeral without parentheses."""
        assert OxidationState.has_oxidation_state(
            "chromium iii"
        ), "Expected has_oxidation_state('chromium iii') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "iron II"
        ), "Expected has_oxidation_state('iron II') to return True, but it returned False"

    def test_has_oxidation_state_with_number(self):
        """Test has_oxidation_state with number."""
        # The new regex requires a sign before the number
        assert OxidationState.has_oxidation_state(
            "iron (+2)"
        ), "Expected has_oxidation_state('iron (+2)') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "iron (-2)"
        ), "Expected has_oxidation_state('iron (-2)') to return True, but it returned False"
        # Numbers without signs or with signs after no longer match
        assert not OxidationState.has_oxidation_state(
            "iron (2)"
        ), "Expected has_oxidation_state('iron (2)') to return False (no sign), but it returned True"
        assert not OxidationState.has_oxidation_state(
            "iron (3+)"
        ), "Expected has_oxidation_state('iron (3+)') to return False (sign after), but it returned True"
        assert not OxidationState.has_oxidation_state(
            "iron (2-)"
        ), "Expected has_oxidation_state('iron (2-)') to return False (sign after), but it returned True"

    def test_has_oxidation_state_with_number_no_parentheses(self):
        """Test has_oxidation_state with number without parentheses."""
        # The new regex requires a sign before the number
        assert OxidationState.has_oxidation_state(
            "iron +3"
        ), "Expected has_oxidation_state('iron +3') to return True, but it returned False"
        assert OxidationState.has_oxidation_state(
            "iron -2"
        ), "Expected has_oxidation_state('iron -2') to return True, but it returned False"
        # Numbers without signs or with signs after no longer match
        assert not OxidationState.has_oxidation_state(
            "iron 2"
        ), "Expected has_oxidation_state('iron 2') to return False (no sign), but it returned True"
        assert not OxidationState.has_oxidation_state(
            "iron 2-"
        ), "Expected has_oxidation_state('iron 2-') to return False (sign after), but it returned True"
        assert not OxidationState.has_oxidation_state(
            "iron 02-"
        ), "Expected has_oxidation_state('iron 02-') to return False (sign after), but it returned True"

    def test_has_oxidation_state_without_oxidation_state(self):
        """Test has_oxidation_state without oxidation state."""
        assert not OxidationState.has_oxidation_state(
            "water"
        ), "Expected has_oxidation_state('water') to return False, but it returned True"
        assert not OxidationState.has_oxidation_state(
            "iron"
        ), "Expected has_oxidation_state('iron') to return False, but it returned True"
        assert not OxidationState.has_oxidation_state(
            "chromium oxide"
        ), "Expected has_oxidation_state('chromium oxide') to return False, but it returned True"

    def test_has_oxidation_state_with_compound_identifier(self):
        """Test has_oxidation_state should not match numbers in compound identifiers."""
        assert not OxidationState.has_oxidation_state(
            "Ethane,, 1,1,2-trichloro-1,2,2-trifluoro-, CFC-113"
        ), "Expected has_oxidation_state('Ethane,, 1,1,2-trichloro-1,2,2-trifluoro-, CFC-113') to return False, but it returned True"

    def test_has_oxidation_state_should_not_match_roman_numeral_in_word(self):
        """Test has_oxidation_state should not match roman numerals embedded in words."""
        assert not OxidationState.has_oxidation_state(
            "Bifenox"
        ), "Expected has_oxidation_state('Bifenox') to return False, but it returned True"

    def test_has_oxidation_state_with_comma(self):
        """Test has_oxidation_state with comma before oxidation state."""
        assert OxidationState.has_oxidation_state(
            "iron, (II)"
        ), "Expected has_oxidation_state('iron, (II)') to return True, but it returned False"
        # The new regex requires a sign before the number
        assert OxidationState.has_oxidation_state(
            "iron, (+2)"
        ), "Expected has_oxidation_state('iron, (+2)') to return True, but it returned False"


class TestOxidationStateFromString:
    """Test OxidationState from_string class method."""

    def test_from_string_with_roman_numeral_lowercase(self):
        """Test from_string with lowercase roman numeral."""
        os, remaining = OxidationState.from_string("chromium (iii)")
        assert os.value == 3, f"Expected os.value to be 3, but got {os.value}"
        assert (
            remaining == "chromium"
        ), f"Expected remaining to be 'chromium', but got {remaining!r}"

    def test_from_string_with_roman_numeral_uppercase(self):
        """Test from_string with uppercase roman numeral."""
        os, remaining = OxidationState.from_string("Iron (II)")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "Iron"
        ), f"Expected remaining to be 'Iron', but got {remaining!r}"

    def test_from_string_with_roman_numeral_no_parentheses(self):
        """Test from_string with roman numeral without parentheses."""
        os, remaining = OxidationState.from_string("chromium iii")
        assert os.value == 3, f"Expected os.value to be 3, but got {os.value}"
        assert (
            remaining == "chromium"
        ), f"Expected remaining to be 'chromium', but got {remaining!r}"

    def test_from_string_with_roman_numeral_negative(self):
        """Test from_string with negative roman numeral."""
        os, remaining = OxidationState.from_string("iron (II-)")
        assert os.value == -2, f"Expected os.value to be -2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_roman_numeral_positive_sign(self):
        """Test from_string with positive sign in roman numeral."""
        os, remaining = OxidationState.from_string("iron (II+)")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number(self):
        """Test from_string with number."""
        # The new regex requires a sign before the number
        os, remaining = OxidationState.from_string("iron (+2)")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number_positive(self):
        """Test from_string with positive number."""
        # The new regex requires a sign before the number
        os, remaining = OxidationState.from_string("iron (+3)")
        assert os.value == 3, f"Expected os.value to be 3, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number_negative(self):
        """Test from_string with negative number."""
        # The new regex requires a sign before the number
        os, remaining = OxidationState.from_string("iron (-2)")
        assert os.value == -2, f"Expected os.value to be -2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number_no_parentheses(self):
        """Test from_string with number without parentheses."""
        # The new regex requires a sign before the number
        os, remaining = OxidationState.from_string("iron +2")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number_sign_before(self):
        """Test from_string with sign before number."""
        os, remaining = OxidationState.from_string("iron +3")
        assert os.value == 3, f"Expected os.value to be 3, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_number_sign_before_negative(self):
        """Test from_string with negative sign before number."""
        os, remaining = OxidationState.from_string("iron -2")
        assert os.value == -2, f"Expected os.value to be -2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_comma(self):
        """Test from_string with comma before oxidation state."""
        os, remaining = OxidationState.from_string("iron, (II)")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_with_comma_and_leading_zeros(self):
        """Test from_string with comma and number with leading zeros."""
        os, remaining = OxidationState.from_string("foo, +002")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "foo"
        ), f"Expected remaining to be 'foo', but got {remaining!r}"

    def test_from_string_with_whitespace(self):
        """Test from_string with whitespace around oxidation state."""
        os, remaining = OxidationState.from_string("iron ( II )")
        assert os.value == 2, f"Expected os.value to be 2, but got {os.value}"
        assert (
            remaining == "iron"
        ), f"Expected remaining to be 'iron', but got {remaining!r}"

    def test_from_string_raises_error_invalid_roman_numeral(self):
        """Test from_string raises error for invalid roman numeral."""
        with pytest.raises(ValueError, match="is not a valid roman numeral"):
            OxidationState.from_string("iron (IIII)")

        # Test various invalid roman numerals
        invalid_cases = [
            "iron (IIII)",  # Four I's in a row
            "iron (VV)",  # Two V's
            "iron (VX)",  # Invalid subtraction
        ]
        for invalid_case in invalid_cases:
            with pytest.raises(ValueError, match="is not a valid roman numeral"):
                OxidationState.from_string(invalid_case)

    def test_from_string_raises_error_both_signs(self):
        """Test from_string raises error when both signs are present."""
        # The new regex only matches signs before the number, so "iron (+2-)" won't match
        with pytest.raises(ValueError, match="No match found"):
            OxidationState.from_string("iron (+2-)")

    def test_from_string_raises_error_no_match(self):
        """Test from_string raises error when no match is found."""
        with pytest.raises(ValueError, match="No match found"):
            OxidationState.from_string("iron")
        with pytest.raises(ValueError, match="No match found"):
            OxidationState.from_string(
                "Ethane,, 1,1,2-trichloro-1,2,2-trifluoro-, CFC-113"
            )
        with pytest.raises(ValueError, match="No match found"):
            OxidationState.from_string("Bifenox")

    def test_from_string_raises_error_too_low(self):
        """Test from_string raises error for value too low."""
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (-6)")

    def test_from_string_raises_error_too_high(self):
        """Test from_string raises error for value too high."""
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (+10)")

    def test_from_string_raises_error_values_outside_bounds_roman(self):
        """Test from_string raises error for roman numeral values outside bounds."""
        # Test values too low
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (VI-)")  # -6

        # Test values too high
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (X)")  # 10
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (XI)")  # 11

    def test_from_string_raises_error_values_outside_bounds_numbers(self):
        """Test from_string raises error for number values outside bounds."""
        # Test values too low
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (-6)")
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (-10)")

        # Test values too high
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (+10)")
        with pytest.raises(ValueError, match="outside physical bounds"):
            OxidationState.from_string("iron (+15)")

    def test_from_string_boundary_values(self):
        """Test from_string with boundary values."""
        os_min, remaining = OxidationState.from_string("iron (-5)")
        assert (
            os_min.value == -5
        ), f"Expected os_min.value to be -5, but got {os_min.value}"

        # The new regex requires a sign before the number
        os_max, remaining = OxidationState.from_string("iron (+9)")
        assert (
            os_max.value == 9
        ), f"Expected os_max.value to be 9, but got {os_max.value}"

    def test_from_string_various_roman_numerals(self):
        """Test from_string with various roman numerals."""
        test_cases = [
            ("iron (i)", 1),
            ("iron (ii)", 2),
            ("iron (iii)", 3),
            ("iron (iv)", 4),
            ("iron (v)", 5),
            ("iron (vi)", 6),
            ("iron (vii)", 7),
            ("iron (viii)", 8),
            ("iron (ix)", 9),
        ]
        for string, expected_value in test_cases:
            os, remaining = OxidationState.from_string(string)
            assert (
                os.value == expected_value
            ), f"Expected os.value to be {expected_value} for '{string}', but got {os.value}"

    def test_from_string_remaining_string(self):
        """Test from_string returns correct remaining string."""
        test_cases = [
            ("chromium (iii)", "chromium"),
            ("iron (II)", "iron"),
            ("manganese (vi)", "manganese"),
            # The new regex requires a sign before the number
            ("mercury (+2)", "mercury"),
            ("tin (+3)", "tin"),
            ("beryllium (-2)", "beryllium"),
        ]
        for string, expected_remaining in test_cases:
            os, remaining = OxidationState.from_string(string)
            assert (
                remaining == expected_remaining
            ), f"Expected remaining to be {expected_remaining!r} for '{string}', but got {remaining!r}"
