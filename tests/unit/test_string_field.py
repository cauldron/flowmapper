"""Unit tests for StringField class."""


from flowmapper.string_field import StringField


class TestStringFieldInitialization:
    """Test StringField initialization."""

    def test_init_with_value(self):
        """Test initialization with a value."""
        sf = StringField("test")
        assert sf == "test", f"Expected sf to equal 'test', but got {sf!r}"
        from collections import UserString
        assert isinstance(sf, UserString), f"Expected sf to be an instance of UserString, but got {type(sf)}"
        assert not isinstance(sf, str), f"Expected sf to not be an instance of str (UserString is not a subclass), but got {type(sf)}"

    def test_init_with_empty_string(self):
        """Test initialization with empty string."""
        sf = StringField("")
        # Empty StringField doesn't equal empty string due to __eq__ implementation
        assert sf != "", f"Expected sf to not equal '', but they are equal (sf={sf!r})"
        assert sf.data == "", f"Expected sf.data to be '', but got {sf.data!r}"

    def test_init_with_whitespace(self):
        """Test initialization with whitespace."""
        sf = StringField("  test  ")
        # Equality normalizes the other string, so "  test  " becomes "test"
        assert sf == "  test  ", f"Expected sf to equal '  test  ', but got {sf!r}"
        assert sf.data == "  test  ", f"Expected sf.data to be '  test  ', but got {sf.data!r}"

    def test_inherits_from_userstring(self):
        """Test that StringField inherits from UserString."""
        sf = StringField("test")
        from collections import UserString
        assert isinstance(sf, UserString), f"Expected sf to be an instance of UserString, but got {type(sf)}"
        assert issubclass(StringField, UserString), "Expected StringField to be a subclass of UserString, but it is not"
        # UserString is not a subclass of str
        assert not isinstance(sf, str), f"Expected sf to not be an instance of str (UserString is not a subclass), but got {type(sf)}"


class TestStringFieldNormalize:
    """Test StringField normalize method."""

    def test_normalize_with_lowercase_default(self):
        """Test normalize with default lowercase=True."""
        sf = StringField("TEST")
        normalized = sf.normalize()
        assert normalized == "test", f"Expected normalized to equal 'test', but got {normalized!r}"
        assert isinstance(normalized, StringField), f"Expected normalized to be a StringField instance, but got {type(normalized)}"

    def test_normalize_with_lowercase_false(self):
        """Test normalize with lowercase=False."""
        sf = StringField("TEST")
        normalized = sf.normalize(lowercase=False)
        assert normalized == "TEST", f"Expected normalized to equal 'TEST', but got {normalized!r}"

    def test_normalize_with_whitespace(self):
        """Test normalize with whitespace."""
        sf = StringField("  test  ")
        normalized = sf.normalize()
        assert normalized == "test", f"Expected normalized to equal 'test', but got {normalized!r}"

    def test_normalize_returns_new_instance(self):
        """Test that normalize returns a new instance."""
        sf = StringField("TEST")
        normalized = sf.normalize()
        assert normalized is not sf, "Expected normalize() to return a new instance, but it returned the same instance"
        assert sf == "TEST", f"Expected original sf to remain 'TEST', but got {sf!r}"


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

    def test_eq_with_string(self):
        """Test equality with string."""
        sf = StringField("test")
        assert sf == "test", f"Expected sf to equal 'test', but they are not equal (sf={sf!r})"
        assert sf != "other", f"Expected sf to not equal 'other', but they are equal (sf={sf!r})"

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


class TestStringFieldStrBehavior:
    """Test StringField string behavior (inherited from str)."""

    def test_str_operations(self):
        """Test that StringField behaves like a string."""
        sf = StringField("test")
        assert len(sf) == 4, f"Expected len(sf) to be 4, but got {len(sf)}"
        assert sf.upper() == "TEST", f"Expected sf.upper() to be 'TEST', but got {sf.upper()!r}"
        assert sf.lower() == "test", f"Expected sf.lower() to be 'test', but got {sf.lower()!r}"
        assert sf.startswith("te"), f"Expected sf.startswith('te') to be True, but got {sf.startswith('te')}"

    def test_bool_with_non_empty_string(self):
        """Test __bool__ with non-empty string (inherited from str)."""
        sf = StringField("test")
        assert bool(sf) is True, f"Expected bool(sf) to be True, but got {bool(sf)}"

    def test_bool_with_empty_string(self):
        """Test __bool__ with empty string (inherited from str)."""
        sf = StringField("")
        assert bool(sf) is False, f"Expected bool(sf) to be False, but got {bool(sf)}"

    def test_bool_with_whitespace(self):
        """Test __bool__ with whitespace-only string (inherited from str)."""
        sf = StringField("   ")
        assert bool(sf) is True, f"Expected bool(sf) to be True for whitespace, but got {bool(sf)}"


class TestStringFieldEdgeCases:
    """Test StringField edge cases."""

    def test_value_preserved_after_normalize(self):
        """Test that original value is preserved after normalize."""
        sf = StringField("ORIGINAL")
        normalized = sf.normalize()
        assert sf == "ORIGINAL", f"Expected original sf to remain 'ORIGINAL', but got {sf!r}"
        assert normalized == "original", f"Expected normalized to be 'original', but got {normalized!r}"

    def test_multiple_normalize_calls(self):
        """Test multiple normalize calls."""
        sf = StringField("  TEST  ")
        norm1 = sf.normalize()
        norm2 = norm1.normalize()
        assert norm1 == "test", f"Expected norm1 to be 'test', but got {norm1!r}"
        assert norm2 == "test", f"Expected norm2 to be 'test', but got {norm2!r}"

    def test_equality_chain(self):
        """Test equality chain with multiple StringFields."""
        sf1 = StringField("test")
        sf2 = StringField("test")
        sf3 = StringField("test")
        assert sf1 == sf2 == sf3, f"Expected all StringFields to be equal, but they are not (sf1={sf1!r}, sf2={sf2!r}, sf3={sf3!r})"

    def test_normalize_with_different_lowercase_settings(self):
        """Test normalize with different lowercase settings."""
        sf = StringField("TEST")
        norm1 = sf.normalize(lowercase=True)
        norm2 = sf.normalize(lowercase=False)
        assert norm1 == "test", f"Expected norm1 to be 'test', but got {norm1!r}"
        assert norm2 == "TEST", f"Expected norm2 to be 'TEST', but got {norm2!r}"

    def test_string_concatenation(self):
        """Test that StringField can be concatenated like a string."""
        sf1 = StringField("hello")
        sf2 = StringField("world")
        result = sf1 + " " + sf2
        assert result == "hello world", f"Expected result to be 'hello world', but got {result!r}"
        # UserString concatenation returns a new instance of the same class
        assert isinstance(result, StringField), f"Expected result to be a StringField instance, but got {type(result)}"
        assert result.data == "hello world", f"Expected result.data to be 'hello world', but got {result.data!r}"

