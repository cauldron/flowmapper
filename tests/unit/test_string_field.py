"""Unit tests for StringField class."""

import pytest

from flowmapper.string_field import StringField


class TestStringFieldInitialization:
    """Test StringField initialization."""

    def test_init_with_value(self):
        """Test initialization with a value."""
        sf = StringField("test")
        assert sf.value == "test", f"Expected sf.value to be 'test', but got {sf.value!r}"
        assert sf.use_lowercase is True, f"Expected sf.use_lowercase to be True, but got {sf.use_lowercase}"

    def test_init_with_value_and_use_lowercase_false(self):
        """Test initialization with use_lowercase=False."""
        sf = StringField("TEST", use_lowercase=False)
        assert sf.value == "TEST", f"Expected sf.value to be 'TEST', but got {sf.value!r}"
        assert sf.use_lowercase is False, f"Expected sf.use_lowercase to be False, but got {sf.use_lowercase}"

    def test_init_with_empty_string(self):
        """Test initialization with empty string."""
        sf = StringField("")
        assert sf.value == "", f"Expected sf.value to be '', but got {sf.value!r}"

    def test_init_with_whitespace(self):
        """Test initialization with whitespace."""
        sf = StringField("  test  ")
        assert sf.value == "  test  ", f"Expected sf.value to be '  test  ', but got {sf.value!r}"


class TestStringFieldNormalize:
    """Test StringField normalize method."""

    def test_normalize_with_lowercase_default(self):
        """Test normalize with default lowercase=True."""
        sf = StringField("TEST")
        normalized = sf.normalize()
        assert normalized.value == "test", f"Expected normalized.value to be 'test', but got {normalized.value!r}"
        assert normalized.use_lowercase is True, f"Expected normalized.use_lowercase to be True, but got {normalized.use_lowercase}"

    def test_normalize_with_lowercase_false(self):
        """Test normalize with use_lowercase=False."""
        sf = StringField("TEST", use_lowercase=False)
        normalized = sf.normalize()
        assert normalized.value == "TEST", f"Expected normalized.value to be 'TEST', but got {normalized.value!r}"
        assert normalized.use_lowercase is False, f"Expected normalized.use_lowercase to be False, but got {normalized.use_lowercase}"

    def test_normalize_with_whitespace(self):
        """Test normalize with whitespace."""
        sf = StringField("  test  ")
        normalized = sf.normalize()
        assert normalized.value == "test", f"Expected normalized.value to be 'test', but got {normalized.value!r}"

    def test_normalize_returns_new_instance(self):
        """Test that normalize returns a new instance."""
        sf = StringField("TEST")
        normalized = sf.normalize()
        assert normalized is not sf, "Expected normalize() to return a new instance, but it returned the same instance"
        assert sf.value == "TEST", f"Expected original sf.value to remain 'TEST', but got {sf.value!r}"


class TestStringFieldEq:
    """Test StringField __eq__ method."""

    def test_eq_with_same_stringfield(self):
        """Test equality with same StringField instance."""
        sf1 = StringField("test")
        sf2 = StringField("test")
        assert sf1 == sf2, f"Expected sf1 to equal sf2, but they are not equal (sf1={sf1!r}, sf2={sf2!r})"

    def test_eq_with_different_stringfield(self):
        """Test equality with different StringField."""
        sf1 = StringField("test")
        sf2 = StringField("other")
        assert sf1 != sf2, f"Expected sf1 to not equal sf2, but they are equal (sf1={sf1!r}, sf2={sf2!r})"

    def test_eq_with_string_lowercase(self):
        """Test equality with string when use_lowercase=True."""
        sf = StringField("TEST", use_lowercase=True)
        assert sf == "test", f"Expected sf to equal 'test', but they are not equal (sf={sf!r})"
        assert sf == "TEST", f"Expected sf to equal 'TEST', but they are not equal (sf={sf!r})"

    def test_eq_with_string_no_lowercase(self):
        """Test equality with string when use_lowercase=False."""
        sf = StringField("TEST", use_lowercase=False)
        assert sf == "TEST", f"Expected sf to equal 'TEST', but they are not equal (sf={sf!r})"
        assert sf != "test", f"Expected sf to not equal 'test', but they are equal (sf={sf!r})"

    def test_eq_with_empty_stringfield(self):
        """Test equality with empty StringField."""
        sf = StringField("")
        assert sf != "", f"Expected sf to not equal '', but they are equal (sf={sf!r})"
        assert sf != "test", f"Expected sf to not equal 'test', but they are equal (sf={sf!r})"

    def test_eq_with_other_type(self):
        """Test equality with non-string, non-StringField type."""
        sf = StringField("test")
        assert sf != 123, f"Expected sf to not equal 123, but they are equal (sf={sf!r})"
        assert sf != None, f"Expected sf to not equal None, but they are equal (sf={sf!r})"
        assert sf != [], f"Expected sf to not equal [], but they are equal (sf={sf!r})"

    def test_eq_with_stringfield_different_lowercase_setting(self):
        """Test equality between StringFields with different use_lowercase settings."""
        sf1 = StringField("TEST", use_lowercase=True)
        sf2 = StringField("TEST", use_lowercase=False)
        # They should be equal because they have the same value
        assert sf1 == sf2, f"Expected sf1 to equal sf2, but they are not equal (sf1={sf1!r}, sf2={sf2!r})"


class TestStringFieldBool:
    """Test StringField __bool__ method."""

    def test_bool_with_non_empty_string(self):
        """Test __bool__ with non-empty string."""
        sf = StringField("test")
        assert bool(sf) is True, f"Expected bool(sf) to be True, but got {bool(sf)}"

    def test_bool_with_empty_string(self):
        """Test __bool__ with empty string."""
        sf = StringField("")
        assert bool(sf) is False, f"Expected bool(sf) to be False, but got {bool(sf)}"

    def test_bool_with_whitespace(self):
        """Test __bool__ with whitespace-only string."""
        sf = StringField("   ")
        assert bool(sf) is True, f"Expected bool(sf) to be True for whitespace, but got {bool(sf)}"


class TestStringFieldRepr:
    """Test StringField __repr__ method."""

    def test_repr_with_value(self):
        """Test __repr__ with a value."""
        sf = StringField("test")
        expected = "StringField: 'test'"
        assert repr(sf) == expected, f"Expected repr(sf) to be {expected!r}, but got {repr(sf)!r}"

    def test_repr_with_empty_string(self):
        """Test __repr__ with empty string."""
        sf = StringField("")
        expected = "StringField with missing value"
        assert repr(sf) == expected, f"Expected repr(sf) to be {expected!r}, but got {repr(sf)!r}"

    def test_repr_with_special_characters(self):
        """Test __repr__ with special characters."""
        sf = StringField("test 'value'")
        expected = "StringField: 'test 'value''"
        assert repr(sf) == expected, f"Expected repr(sf) to be {expected!r}, but got {repr(sf)!r}"

    def test_repr_with_unicode(self):
        """Test __repr__ with unicode characters."""
        sf = StringField("café")
        expected = "StringField: 'café'"
        assert repr(sf) == expected, f"Expected repr(sf) to be {expected!r}, but got {repr(sf)!r}"


class TestStringFieldEdgeCases:
    """Test StringField edge cases."""

    def test_value_preserved_after_normalize(self):
        """Test that original value is preserved after normalize."""
        sf = StringField("ORIGINAL")
        normalized = sf.normalize()
        assert sf.value == "ORIGINAL", f"Expected original sf.value to remain 'ORIGINAL', but got {sf.value!r}"
        assert normalized.value == "original", f"Expected normalized.value to be 'original', but got {normalized.value!r}"

    def test_multiple_normalize_calls(self):
        """Test multiple normalize calls."""
        sf = StringField("  TEST  ")
        norm1 = sf.normalize()
        norm2 = norm1.normalize()
        assert norm1.value == "test", f"Expected norm1.value to be 'test', but got {norm1.value!r}"
        assert norm2.value == "test", f"Expected norm2.value to be 'test', but got {norm2.value!r}"

    def test_equality_chain(self):
        """Test equality chain with multiple StringFields."""
        sf1 = StringField("test")
        sf2 = StringField("test")
        sf3 = StringField("test")
        assert sf1 == sf2 == sf3, f"Expected all StringFields to be equal, but they are not (sf1={sf1!r}, sf2={sf2!r}, sf3={sf3!r})"

    def test_equality_with_normalized(self):
        """Test equality between original and normalized StringField."""
        sf1 = StringField("TEST")
        sf2 = sf1.normalize()
        # They should be equal because they have the same value after normalization
        assert sf1 == sf2, f"Expected sf1 to equal normalized sf2, but they are not equal (sf1={sf1!r}, sf2={sf2!r})"

