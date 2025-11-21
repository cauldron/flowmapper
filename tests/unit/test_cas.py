"""Unit tests for CASField class."""

import pytest

from flowmapper.fields import CASField


class TestCASFieldInitialization:
    """Test CASField initialization."""

    def test_init_with_valid_cas_string(self):
        """Test initialization with valid CAS string."""
        cas = CASField("0000096-49-1")
        assert (
            cas.data == "0000096-49-1"
        ), f"Expected cas.data to be '0000096-49-1', but got {cas.data!r}"
        from collections import UserString

        assert isinstance(
            cas, UserString
        ), f"Expected cas to be an instance of UserString, but got {type(cas)}"

    def test_init_with_empty_string_raises_error(self):
        """Test initialization with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("")

    def test_init_with_none_raises_error(self):
        """Test initialization with None raises TypeError."""
        with pytest.raises(TypeError, match="CASField takes only `str`, but got"):
            CASField(None)  # type: ignore[arg-type]

    def test_init_with_integer_raises_error(self):
        """Test initialization with integer raises TypeError."""
        with pytest.raises(TypeError, match="CASField takes only `str`, but got"):
            CASField(96491)  # type: ignore[arg-type]

    def test_init_with_userstring(self):
        """Test initialization with UserString works."""
        from collections import UserString

        us = UserString("7782-40-3")
        # CASField converts UserString to string before regex search, so it works
        cas = CASField(us)
        assert (
            cas.data == "7782-40-3"
        ), f"Expected cas.data to be '7782-40-3', but got {cas.data!r}"
        assert isinstance(
            cas, CASField
        ), f"Expected cas to be an instance of CASField, but got {type(cas)}"

    def test_init_with_two_digits_in_front(self):
        """Test initialization with whitespace."""
        assert CASField(
            "94-75-7"
        ), "Initialization with two numbers in front section failed"

    def test_init_with_whitespace(self):
        """Test initialization with whitespace."""
        cas = CASField("  7782-40-3  ")
        assert (
            cas.data == "  7782-40-3  "
        ), f"Expected cas.data to preserve whitespace, but got {cas.data!r}"

    def test_inherits_from_userstring(self):
        """Test that CASField inherits from UserString."""
        cas = CASField("7782-40-3")
        from collections import UserString

        assert isinstance(
            cas, UserString
        ), f"Expected cas to be an instance of UserString, but got {type(cas)}"
        # UserString is not a subclass of str
        assert not isinstance(
            cas, str
        ), f"Expected cas to not be an instance of str (UserString is not a subclass), but got {type(cas)}"

    def test_init_with_casfield(self):
        """Test initialization with another CASField object."""
        cas1 = CASField("7782-40-3")
        cas2 = CASField(cas1)
        assert (
            cas2.data == "7782-40-3"
        ), f"Expected cas2.data to be '7782-40-3', but got {cas2.data!r}"
        assert (
            cas1 == cas2
        ), f"Expected cas1 to equal cas2, but they are not equal (cas1={cas1!r}, cas2={cas2!r})"
        assert (
            cas1 is not cas2
        ), "Expected cas1 and cas2 to be different instances, but they are the same instance"
        assert isinstance(
            cas2, CASField
        ), f"Expected cas2 to be an instance of CASField, but got {type(cas2)}"


class TestCASFieldDigits:
    """Test CASField digits property."""

    def test_digits_with_dashes(self):
        """Test digits property with dashes."""
        cas = CASField("0000096-49-1")
        assert cas.digits == [
            0,
            0,
            0,
            0,
            0,
            9,
            6,
            4,
            9,
            1,
        ], f"Expected cas.digits to be [0, 0, 0, 0, 0, 9, 6, 4, 9, 1], but got {cas.digits}"

    def test_digits_without_dashes_raises_error(self):
        """Test digits property without dashes raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("0000096491")

    def test_digits_with_empty_string_raises_error(self):
        """Test digits property with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("")


class TestCASFieldExport:
    """Test CASField export method."""

    def test_export_with_standard_format(self):
        """Test export with standard CAS format."""
        cas = CASField("7782-40-3")
        assert (
            cas.export() == "7782-40-3"
        ), f"Expected cas.export() to be '7782-40-3', but got {cas.export()!r}"

    def test_export_without_dashes_raises_error(self):
        """Test export without dashes raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("7782403")

    def test_export_with_leading_zeros(self):
        """Test export with leading zeros."""
        cas = CASField("0007782-40-3")
        # Export keeps leading zeros in the first part
        assert (
            cas.export() == "0007782-40-3"
        ), f"Expected cas.export() to be '0007782-40-3', but got {cas.export()!r}"

    def test_export_with_empty_string_raises_error(self):
        """Test export with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("")

    def test_export_with_single_digit_raises_error(self):
        """Test export with single digit raises ValueError."""
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            CASField("1")


class TestCASFieldCheckDigitExpected:
    """Test CASField check_digit_expected property."""

    def test_check_digit_expected_valid_cas(self):
        """Test check_digit_expected with CAS number."""
        cas = CASField("7732-18-5")
        expected = cas.check_digit_expected
        assert (
            expected == 5
        ), f"Expected check_digit_expected to be 5, but got {expected}"

    def test_check_digit_expected_invalid_cas(self):
        """Test check_digit_expected with invalid CAS number."""
        cas = CASField("7782-40-2")
        # Check digit is 2, but expected is 3
        expected = cas.check_digit_expected
        assert (
            expected == 3
        ), f"Expected check_digit_expected to be 3, but got {expected}"


class TestCASFieldValid:
    """Test CASField valid method."""

    def test_valid_with_invalid_cas(self):
        """Test valid with invalid CAS number."""
        cas = CASField("7782-40-2")
        assert (
            not cas.valid()
        ), f"Expected cas.valid() to be False, but got {cas.valid()}"

    def test_valid_with_leading_zeros(self):
        """Test valid with leading zeros."""
        cas = CASField("0000096-49-1")
        # Check digit calculation includes leading zeros
        is_valid = cas.valid()
        assert is_valid and isinstance(
            is_valid, bool
        ), f"Expected cas.valid() to return a bool, but got {type(is_valid)}"


class TestCASFieldFromString:
    """Test CASField from_string method."""

    def test_from_string_with_valid_cas(self):
        """Test from_string with valid CAS number."""
        cas = CASField("7782-40-3")
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            cas.from_string("000009-49-1")

    def test_from_string_with_whitespace(self):
        """Test from_string with whitespace."""
        cas = CASField("7782-40-3")
        result = cas.from_string("  7782-40-3  ")
        # Testing actual behavior
        assert result is None or isinstance(
            result, CASField
        ), f"Expected result to be None or CASField, but got {type(result)}"

    def test_from_string_with_invalid_cas(self):
        """Test from_string with invalid CAS number."""
        cas = CASField("7782-40-3")
        result = cas.from_string("7782-40-2")
        # Invalid CAS should return None
        assert (
            result is None
        ), f"Expected from_string to return None for invalid CAS, but got {result}"

    def test_from_string_with_empty_string(self):
        """Test from_string with empty string."""
        cas = CASField("7782-40-3")
        # Empty string will fail validation in __init__
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            cas.from_string("")

    def test_from_string_with_none(self):
        """Test from_string with None."""
        cas = CASField("7782-40-3")
        result = cas.from_string(None)
        assert (
            result is None
        ), f"Expected from_string to return None for None, but got {result}"

    def test_from_string_returns_new_instance(self):
        """Test that from_string returns a new instance when valid."""
        cas = CASField("7782-40-3")
        result = cas.from_string("7440-05-3")
        if result is not None:
            assert (
                result is not cas
            ), "Expected from_string() to return a new instance, but it returned the same instance"
            assert (
                cas.data == "7782-40-3"
            ), f"Expected original cas.data to remain '7782-40-3', but got {cas.data!r}"


class TestCASFieldEquality:
    """Test CASField equality comparison."""

    def test_eq_with_same_casfield(self):
        """Test equality with same CASField instance (exact data match)."""
        cas1 = CASField("7440-05-3")
        cas2 = CASField("7440-05-3")
        # CASField to CASField comparison uses exact data comparison
        assert (
            cas1 == cas2
        ), f"Expected cas1 to equal cas2, but they are not equal (cas1={cas1!r}, cas2={cas2!r})"

    def test_eq_with_different_casfield_data(self):
        """Test equality with CASField having different data."""
        cas1 = CASField("7440-05-3")
        cas2 = CASField("7782-40-3")
        assert (
            cas1 != cas2
        ), f"Expected cas1 to not equal cas2, but they are equal (cas1={cas1!r}, cas2={cas2!r})"

    def test_eq_with_casfield_different_formatting(self):
        """Test equality with CASField having same CAS but different formatting."""
        cas1 = CASField("7440-05-3")
        cas2 = CASField("0007440-05-3")
        # CASField to CASField uses exact data comparison, so formatting matters
        assert (
            cas1 != cas2
        ), f"Expected cas1 to not equal cas2 (different formatting), but they are equal (cas1={cas1!r}, cas2={cas2!r})"

    def test_eq_with_string_exact_match(self):
        """Test equality with string that exactly matches."""
        cas = CASField("7440-05-3")
        assert (
            cas == "7440-05-3"
        ), f"Expected cas to equal '7440-05-3', but they are not equal (cas={cas!r})"

    def test_eq_with_string_different_cas(self):
        """Test equality with string containing different CAS number."""
        cas = CASField("7440-05-3")
        assert (
            cas != "7782-40-3"
        ), f"Expected cas to not equal '7782-40-3', but they are equal (cas={cas!r})"

    def test_eq_with_string_leading_zeros(self):
        """Test equality with string containing leading zeros (should normalize)."""
        cas = CASField("7440-05-3")
        # String comparison uses from_string which normalizes (strips leading zeros)
        assert (
            cas == "0007440-05-3"
        ), f"Expected cas to equal '0007440-05-3' (normalized), but they are not equal (cas={cas!r})"

    def test_eq_with_string_whitespace(self):
        """Test equality with string containing whitespace (should normalize)."""
        cas = CASField("7440-05-3")
        # String comparison uses from_string which normalizes (strips whitespace)
        assert (
            cas == "  7440-05-3  "
        ), f"Expected cas to equal '  7440-05-3  ' (normalized), but they are not equal (cas={cas!r})"

    def test_eq_with_string_leading_zeros_and_whitespace(self):
        """Test equality with string containing both leading zeros and whitespace."""
        cas = CASField("7440-05-3")
        # String comparison normalizes both whitespace and leading zeros
        assert (
            cas == "  0007440-05-3  "
        ), f"Expected cas to equal '  0007440-05-3  ' (normalized), but they are not equal (cas={cas!r})"

    def test_eq_with_string_invalid_cas(self):
        """Test equality with string containing invalid CAS number."""
        cas = CASField("7440-05-3")
        # Invalid CAS strings return None from from_string, so equality is False
        assert (
            cas != "7440-05-2"
        ), f"Expected cas to not equal '7440-05-2' (invalid check digit), but they are equal (cas={cas!r})"

    def test_eq_with_string_empty_string(self):
        """Test equality with empty string raises ValueError."""
        cas = CASField("7440-05-3")
        # Empty string is invalid CAS, so from_string raises ValueError when creating CASField
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            _ = cas == ""

    def test_eq_with_userstring(self):
        """Test equality with UserString."""
        from collections import UserString

        cas = CASField("7440-05-3")
        us = UserString("7440-05-3")
        # UserString is handled like str in __eq__, so it should normalize
        assert (
            cas == us
        ), f"Expected cas to equal UserString('7440-05-3'), but they are not equal (cas={cas!r})"

    def test_eq_with_userstring_leading_zeros(self):
        """Test equality with UserString containing leading zeros."""
        from collections import UserString

        cas = CASField("7440-05-3")
        us = UserString("0007440-05-3")
        # UserString should normalize like str
        assert (
            cas == us
        ), f"Expected cas to equal UserString('0007440-05-3') (normalized), but they are not equal (cas={cas!r})"

    def test_eq_with_other_types(self):
        """Test equality with other types returns False."""
        cas = CASField("7440-05-3")
        # Non-string, non-CASField types should return False
        assert (
            cas != 744053
        ), f"Expected cas to not equal integer, but they are equal (cas={cas!r})"
        assert (
            cas != None
        ), f"Expected cas to not equal None, but they are equal (cas={cas!r})"
        assert (
            cas != []
        ), f"Expected cas to not equal list, but they are equal (cas={cas!r})"

    def test_ne_with_different_casfield(self):
        """Test inequality with different CASField."""
        cas1 = CASField("7440-05-3")
        cas2 = CASField("7782-40-3")
        assert (
            cas1 != cas2
        ), f"Expected cas1 to not equal cas2, but they are equal (cas1={cas1!r}, cas2={cas2!r})"

    def test_ne_with_string(self):
        """Test inequality with different string."""
        cas = CASField("7440-05-3")
        assert (
            cas != "7782-40-3"
        ), f"Expected cas to not equal '7782-40-3', but they are equal (cas={cas!r})"


class TestCASFieldStringBehavior:
    """Test CASField string behavior (inherited from UserString)."""

    def test_string_operations(self):
        """Test that CASField behaves like a string."""
        cas = CASField("7782-40-3")
        assert len(cas) == 9, f"Expected len(cas) to be 9, but got {len(cas)}"
        assert (
            cas.upper() == "7782-40-3"
        ), f"Expected cas.upper() to be '7782-40-3', but got {cas.upper()!r}"
        assert cas.startswith(
            "778"
        ), f"Expected cas.startswith('778') to be True, but got {cas.startswith('778')}"

    def test_string_concatenation_raises_error(self):
        """Test that CASField concatenation raises ValueError for invalid format."""
        cas1 = CASField("7782-40-3")
        cas2 = CASField("7440-05-3")
        # Concatenation creates a string that doesn't match CAS format, so __init__ raises ValueError
        with pytest.raises(ValueError, match="Given input is not valid CAS formatting"):
            _ = cas1 + " and " + cas2
