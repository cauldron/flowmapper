"""Unit tests for ContextField class."""

import pytest

from flowmapper.fields import ContextField
from flowmapper.utils import MISSING_VALUES


class TestContextFieldInitialization:
    """Test ContextField initialization."""

    def test_init_with_string(self):
        """Test initialization with string."""
        c = ContextField("Raw/(unspecified)")
        assert (
            c.value == "Raw/(unspecified)"
        ), f"Expected c.value to be 'Raw/(unspecified)', but got {c.value!r}"
        assert isinstance(
            c.value, str
        ), f"Expected c.value to be a str, but got {type(c.value)}"

    def test_init_with_list(self):
        """Test initialization with list."""
        c = ContextField(["Raw", "(unspecified)"])
        assert c.value == [
            "Raw",
            "(unspecified)",
        ], f"Expected c.value to be ['Raw', '(unspecified)'], but got {c.value!r}"
        assert isinstance(
            c.value, list
        ), f"Expected c.value to be a list, but got {type(c.value)}"

    def test_init_with_tuple(self):
        """Test initialization with tuple."""
        c = ContextField(("Raw",))
        assert c.value == (
            "Raw",
        ), f"Expected c.value to be ('Raw',), but got {c.value!r}"
        assert isinstance(
            c.value, tuple
        ), f"Expected c.value to be a tuple, but got {type(c.value)}"

    def test_init_with_empty_string(self):
        """Test initialization with empty string."""
        c = ContextField("")
        assert c.value == "", f"Expected c.value to be '', but got {c.value!r}"

    def test_init_with_empty_list(self):
        """Test initialization with empty list."""
        c = ContextField([])
        assert c.value == [], f"Expected c.value to be [], but got {c.value!r}"

    def test_init_with_empty_tuple(self):
        """Test initialization with empty tuple."""
        c = ContextField(tuple([]))
        assert c.value == (), f"Expected c.value to be (), but got {c.value!r}"


class TestContextFieldNormalize:
    """Test ContextField normalize method."""

    def test_normalize_with_string(self):
        """Test normalize with string value."""
        c = ContextField("A/B")
        normalized = c.normalize()
        assert normalized.value == (
            "a",
            "b",
        ), f"Expected normalized.value to be ('a', 'b'), but got {normalized.value!r}"
        assert isinstance(
            normalized.value, tuple
        ), f"Expected normalized.value to be a tuple, but got {type(normalized.value)}"
        assert (
            c.value == "A/B"
        ), f"Expected original c.value to remain 'A/B', but got {c.value!r}"

    def test_normalize_with_string_no_slash(self):
        """Test normalize with string without slash."""
        c = ContextField("A-B")
        normalized = c.normalize()
        assert normalized.value == (
            "a-b",
        ), f"Expected normalized.value to be ('a-b',), but got {normalized.value!r}"

    def test_normalize_with_list(self):
        """Test normalize with list value."""
        c = ContextField(["Raw", "(unspecified)"])
        normalized = c.normalize()
        assert normalized.value == (
            "raw",
        ), f"Expected normalized.value to be ('raw',), but got {normalized.value!r}"

    def test_normalize_with_only_unspecified(self):
        """Test normalize with only unspecified value."""
        # When the only value is unspecified, it should be kept
        c = ContextField(["unspecified"])
        normalized = c.normalize()
        assert normalized.value == (
            "unspecified",
        ), f"Expected normalized.value to be ('unspecified',), but got {normalized.value!r}"

        # Test with (unspecified) in parentheses
        c2 = ContextField(["(unspecified)"])
        normalized2 = c2.normalize()
        assert normalized2.value == (
            "(unspecified)",
        ), f"Expected normalized.value to be ('(unspecified)',), but got {normalized2.value!r}"

        # Test with string "unspecified"
        c3 = ContextField("unspecified")
        normalized3 = c3.normalize()
        assert normalized3.value == (
            "unspecified",
        ), f"Expected normalized.value to be ('unspecified',), but got {normalized3.value!r}"

        # Test with multipleunspecified in parentheses
        c2 = ContextField(["(unspecified)", "(unspecified)"])
        normalized2 = c2.normalize()
        assert normalized2.value == (
            "(unspecified)",
        ), f"Expected normalized.value to be ('(unspecified)',), but got {normalized2.value!r}"

    def test_normalize_with_tuple(self):
        """Test normalize with tuple value."""
        c = ContextField(("Raw",))
        normalized = c.normalize()
        assert normalized.value == (
            "raw",
        ), f"Expected normalized.value to be ('raw',), but got {normalized.value!r}"

    def test_normalize_with_obj_parameter(self):
        """Test normalize with obj parameter."""
        c = ContextField("X/Y")
        normalized = c.normalize("A/B")
        assert normalized.value == (
            "a",
            "b",
        ), f"Expected normalized.value to be ('a', 'b'), but got {normalized.value!r}"
        assert (
            c.value == "X/Y"
        ), f"Expected original c.value to remain 'X/Y', but got {c.value!r}"

    def test_normalize_lowercase(self):
        """Test normalize converts to lowercase."""
        c = ContextField("A-B")
        normalized = c.normalize()
        assert normalized.value == (
            "a-b",
        ), f"Expected normalized.value to be ('a-b',), but got {normalized.value!r}"

    def test_normalize_strip(self):
        """Test normalize strips whitespace."""
        c = ContextField(" A-B\t\n")
        normalized = c.normalize()
        assert normalized.value == (
            "a-b",
        ), f"Expected normalized.value to be ('a-b',), but got {normalized.value!r}"

    def test_normalize_removes_trailing_missing_values(self):
        """Test normalize removes trailing missing values."""
        c = ContextField(("A", "(unknown)"))
        normalized = c.normalize()
        assert normalized.value == (
            "a",
        ), f"Expected normalized.value to be ('a',), but got {normalized.value!r}"

    @pytest.mark.parametrize("missing_value", MISSING_VALUES)
    def test_normalize_removes_trailing_missing_value(self, missing_value):
        """Test normalize removes trailing missing values."""
        c = ContextField(("A", missing_value))
        normalized = c.normalize()
        assert normalized.value == (
            "a",
        ), f"Expected normalized.value to be ('a',) for missing value {missing_value!r}, but got {normalized.value!r}"

    def test_normalize_removes_multiple_trailing_missing_values(self):
        """Test normalize removes multiple trailing missing values."""
        c = ContextField(("A", "(unknown)", "(unspecified)"))
        normalized = c.normalize()
        assert normalized.value == (
            "a",
        ), f"Expected normalized.value to be ('a',), but got {normalized.value!r}"

    def test_normalize_does_not_remove_leading_missing_values(self):
        """Test normalize does not remove leading missing values."""
        c = ContextField(("(unknown)", "A"))
        normalized = c.normalize()
        assert normalized.value == (
            "(unknown)",
            "a",
        ), f"Expected normalized.value to be ('(unknown)', 'a'), but got {normalized.value!r}"

    def test_normalize_returns_new_instance(self):
        """Test that normalize returns a new instance."""
        c = ContextField("A/B")
        normalized = c.normalize()
        assert (
            normalized is not c
        ), "Expected normalize() to return a new instance, but it returned the same instance"
        assert (
            c.value == "A/B"
        ), f"Expected original c.value to remain 'A/B', but got {c.value!r}"

    def test_normalize_with_invalid_type_raises_error(self):
        """Test normalize with invalid type raises ValueError."""

        class Foo:
            pass

        c = ContextField("A/B")
        with pytest.raises(ValueError, match="Can't understand input context"):
            c.normalize(Foo())


class TestContextFieldExportAsString:
    """Test ContextField export_as_string method."""

    def test_export_as_string_with_list(self):
        """Test export_as_string with list value."""
        c = ContextField(["A", "B"])
        result = c.export_as_string()
        assert (
            result == "A✂️B"
        ), f"Expected export_as_string() to be 'A✂️B', but got {result!r}"

    def test_export_as_string_with_tuple(self):
        """Test export_as_string with tuple value."""
        c = ContextField(("A", "B"))
        result = c.export_as_string()
        assert (
            result == "A✂️B"
        ), f"Expected export_as_string() to be 'A✂️B', but got {result!r}"

    def test_export_as_string_with_string(self):
        """Test export_as_string with string value."""
        c = ContextField("A/B")
        result = c.export_as_string()
        assert (
            result == "A/B"
        ), f"Expected export_as_string() to be 'A/B', but got {result!r}"

    def test_export_as_string_with_custom_join_character_list(self):
        """Test export_as_string with custom join_character for list value."""
        c = ContextField(["A", "B"])
        result = c.export_as_string("/")
        assert (
            result == "A/B"
        ), f"Expected export_as_string('/') to be 'A/B', but got {result!r}"

    def test_export_as_string_with_custom_join_character_tuple(self):
        """Test export_as_string with custom join_character for tuple value."""
        c = ContextField(("A", "B", "C"))
        result = c.export_as_string("|")
        assert (
            result == "A|B|C"
        ), f"Expected export_as_string('|') to be 'A|B|C', but got {result!r}"

    def test_export_as_string_with_custom_join_character_dash(self):
        """Test export_as_string with custom join_character '-'."""
        c = ContextField(["A", "B"])
        result = c.export_as_string("-")
        assert (
            result == "A-B"
        ), f"Expected export_as_string('-') to be 'A-B', but got {result!r}"

    def test_export_as_string_with_custom_join_character_string_value(self):
        """Test export_as_string with custom join_character for string value (should not use join_character)."""
        c = ContextField("A/B")
        result = c.export_as_string("/")
        # String values are returned as-is, join_character is not used
        assert (
            result == "A/B"
        ), f"Expected export_as_string('/') to be 'A/B' for string value, but got {result!r}"

    def test_export_as_string_with_custom_join_character_empty_string(self):
        """Test export_as_string with custom join_character as empty string."""
        c = ContextField(["A", "B"])
        result = c.export_as_string("")
        assert (
            result == "AB"
        ), f"Expected export_as_string('') to be 'AB', but got {result!r}"

    def test_export_as_string_with_custom_join_character_space(self):
        """Test export_as_string with custom join_character as space."""
        c = ContextField(["A", "B", "C"])
        result = c.export_as_string(" ")
        assert (
            result == "A B C"
        ), f"Expected export_as_string(' ') to be 'A B C', but got {result!r}"


class TestContextFieldEq:
    """Test ContextField __eq__ method."""

    def test_eq_with_same_contextfield(self):
        """Test equality with same ContextField instance."""
        c1 = ContextField("A/B")
        c2 = ContextField("A/B")
        assert (
            c1 == c2
        ), f"Expected c1 to equal c2, but they are not equal (c1={c1!r}, c2={c2!r})"

    def test_eq_with_different_contextfield(self):
        """Test equality with different ContextField."""
        c1 = ContextField("A/B")
        c2 = ContextField("X/Y")
        assert (
            c1 != c2
        ), f"Expected c1 to not equal c2, but they are equal (c1={c1!r}, c2={c2!r})"

    def test_eq_with_list_and_string(self):
        """Test equality with list and string values."""
        c1 = ContextField("A/B")
        c2 = ContextField(["A", "B"])
        # Different value types, so not equal
        assert (
            c1 != c2
        ), f"Expected c1 to not equal c2, but they are equal (c1={c1!r}, c2={c2!r})"

    def test_eq_with_string_other(self):
        """Test equality with string other."""
        c = ContextField("A/B")
        # __eq__ normalizes the other value and compares
        # "A/B" normalized is ('a', 'b'), but c.value is "A/B", so not equal
        assert (
            c != "A/B"
        ), f"Expected c to not equal 'A/B', but they are equal (c={c!r})"

    def test_eq_with_empty_contextfield(self):
        """Test equality with empty ContextField."""
        c1 = ContextField("")
        c2 = ContextField("")
        # Empty strings are falsy, so __eq__ goes to else branch
        # Empty string normalizes to ('',), so c1.value ("") != normalized c2.value (('',))
        assert (
            c1 != c2
        ), f"Expected c1 to not equal c2 for empty strings, but they are equal (c1={c1!r}, c2={c2!r})"

    def test_eq_with_other_type(self):
        """Test equality with non-ContextField type."""
        c = ContextField("A/B")
        assert c != 123, f"Expected c to not equal 123, but they are equal (c={c!r})"
        assert c != None, f"Expected c to not equal None, but they are equal (c={c!r})"
        assert c != [], f"Expected c to not equal [], but they are equal (c={c!r})"


class TestContextFieldBool:
    """Test ContextField __bool__ method."""

    def test_bool_with_non_empty_string(self):
        """Test __bool__ with non-empty string."""
        c = ContextField("A/B")
        assert bool(c) is True, f"Expected bool(c) to be True, but got {bool(c)}"

    def test_bool_with_empty_string(self):
        """Test __bool__ with empty string."""
        c = ContextField("")
        assert bool(c) is False, f"Expected bool(c) to be False, but got {bool(c)}"

    def test_bool_with_non_empty_list(self):
        """Test __bool__ with non-empty list."""
        c = ContextField(["A", "B"])
        assert bool(c) is True, f"Expected bool(c) to be True, but got {bool(c)}"

    def test_bool_with_empty_list(self):
        """Test __bool__ with empty list."""
        c = ContextField([])
        assert bool(c) is False, f"Expected bool(c) to be False, but got {bool(c)}"

    def test_bool_with_non_empty_tuple(self):
        """Test __bool__ with non-empty tuple."""
        c = ContextField(("A",))
        assert bool(c) is True, f"Expected bool(c) to be True, but got {bool(c)}"

    def test_bool_with_empty_tuple(self):
        """Test __bool__ with empty tuple."""
        c = ContextField(())
        assert bool(c) is False, f"Expected bool(c) to be False, but got {bool(c)}"


class TestContextFieldHash:
    """Test ContextField __hash__ method."""

    def test_hash_with_string(self):
        """Test __hash__ with string value."""
        c = ContextField("A/B")
        result = hash(c)
        assert isinstance(
            result, int
        ), f"Expected hash(c) to be an int, but got {type(result)}"

    def test_hash_with_list_raises_error(self):
        """Test __hash__ with list value raises TypeError."""
        c = ContextField(["A", "B"])
        # Lists are not hashable, so hash() raises TypeError
        with pytest.raises(TypeError):
            _ = hash(c)

    def test_hash_with_tuple(self):
        """Test __hash__ with tuple value."""
        c = ContextField(("A", "B"))
        result = hash(c)
        assert isinstance(
            result, int
        ), f"Expected hash(c) to be an int, but got {type(result)}"

    def test_hash_same_values(self):
        """Test __hash__ with same values."""
        c1 = ContextField("A/B")
        c2 = ContextField("A/B")
        assert hash(c1) == hash(
            c2
        ), f"Expected hash(c1) to equal hash(c2), but got {hash(c1)} and {hash(c2)}"


class TestContextFieldIter:
    """Test ContextField __iter__ method."""

    def test_iter_with_string(self):
        """Test __iter__ with string value."""
        c = ContextField("A/B")
        result = list(c)
        assert result == [
            "A",
            "/",
            "B",
        ], f"Expected list(c) to be ['A', '/', 'B'], but got {result!r}"

    def test_iter_with_list(self):
        """Test __iter__ with list value."""
        c = ContextField(["A", "B"])
        result = list(c)
        assert result == [
            "A",
            "B",
        ], f"Expected list(c) to be ['A', 'B'], but got {result!r}"

    def test_iter_with_tuple(self):
        """Test __iter__ with tuple value."""
        c = ContextField(("A", "B"))
        result = list(c)
        assert result == [
            "A",
            "B",
        ], f"Expected list(c) to be ['A', 'B'], but got {result!r}"


class TestContextFieldContains:
    """Test ContextField __contains__ method."""

    def test_contains_with_string_values(self):
        """Test __contains__ with string values."""
        c1 = ContextField("A")
        c2 = ContextField("A/B")
        # c2 in c1 means c1 is more generic than c2
        # This checks if c1.value == c2.value[:len(c1.value)]
        # "A" == "A/B"[:1] -> "A" == "A" -> True
        assert (
            c2 in c1
        ), f"Expected c2 to be in c1, but it was not (c1={c1!r}, c2={c2!r})"
        assert (
            c1 not in c2
        ), f"Expected c1 to not be in c2, but it was (c1={c1!r}, c2={c2!r})"

    def test_contains_with_tuple_values(self):
        """Test __contains__ with tuple values."""
        c1 = ContextField(("A",))
        c2 = ContextField(("A", "B"))
        # c2 in c1 means c1 is more generic than c2
        # This checks if c1.value == c2.value[:len(c1.value)]
        # ("A",) == ("A", "B")[:1] -> ("A",) == ("A",) -> True
        assert (
            c2 in c1
        ), f"Expected c2 to be in c1, but it was not (c1={c1!r}, c2={c2!r})"
        assert (
            c1 not in c2
        ), f"Expected c1 to not be in c2, but it was (c1={c1!r}, c2={c2!r})"

    def test_contains_with_list_values(self):
        """Test __contains__ with list values."""
        c1 = ContextField(["A"])
        c2 = ContextField(["A", "B"])
        # c2 in c1 means c1 is more generic than c2
        assert (
            c2 in c1
        ), f"Expected c2 to be in c1, but it was not (c1={c1!r}, c2={c2!r})"
        assert (
            c1 not in c2
        ), f"Expected c1 to not be in c2, but it was (c1={c1!r}, c2={c2!r})"

    def test_contains_with_non_contextfield(self):
        """Test __contains__ with non-ContextField returns False."""
        c = ContextField("A/B")
        assert "A/B" not in c, f"Expected 'A/B' to not be in c, but it was (c={c!r})"
        assert 123 not in c, f"Expected 123 to not be in c, but it was (c={c!r})"


class TestContextFieldRepr:
    """Test ContextField __repr__ method."""

    def test_repr_with_string(self):
        """Test __repr__ with string value."""
        c = ContextField("A/B")
        result = repr(c)
        assert result == "A/B", f"Expected repr(c) to be 'A/B', but got {result!r}"

    def test_repr_with_list(self):
        """Test __repr__ with list value."""
        c = ContextField(["A", "B"])
        result = repr(c)
        assert (
            result == "['A', 'B']"
        ), f"Expected repr(c) to be '['A', 'B']', but got {result!r}"

    def test_repr_with_tuple(self):
        """Test __repr__ with tuple value."""
        c = ContextField(("A", "B"))
        result = repr(c)
        assert (
            result == "('A', 'B')"
        ), f"Expected repr(c) to be '('A', 'B')', but got {result!r}"


class TestContextFieldEdgeCases:
    """Test ContextField edge cases."""

    def test_normalize_preserves_original_value(self):
        """Test that normalize preserves original value."""
        c = ContextField("ORIGINAL")
        normalized = c.normalize()
        assert (
            c.value == "ORIGINAL"
        ), f"Expected original c.value to remain 'ORIGINAL', but got {c.value!r}"
        assert normalized.value == (
            "original",
        ), f"Expected normalized.value to be ('original',), but got {normalized.value!r}"

    def test_multiple_normalize_calls(self):
        """Test multiple normalize calls."""
        c = ContextField("  TEST  ")
        norm1 = c.normalize()
        norm2 = norm1.normalize()
        assert norm1.value == (
            "test",
        ), f"Expected norm1.value to be ('test',), but got {norm1.value!r}"
        assert norm2.value == (
            "test",
        ), f"Expected norm2.value to be ('test',), but got {norm2.value!r}"

    def test_normalize_with_mapping_parameter(self):
        """Test normalize with mapping parameter (currently not implemented)."""
        c = ContextField("A/B")
        # mapping parameter is accepted but not used (TODO in code)
        normalized = c.normalize(mapping={"A": "X"})
        assert normalized.value == (
            "a",
            "b",
        ), f"Expected normalized.value to be ('a', 'b'), but got {normalized.value!r}"


class TestContextFieldIsResource:
    """Test ContextField is_resource method."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            # String values that should return True (resource categories)
            ("resource", True),
            ("resources", True),
            ("natural resource", True),
            ("natural resources", True),
            ("land use", True),
            ("economic", True),
            ("social", True),
            ("raw materials", True),
            ("raw", True),
            # Case insensitivity
            ("RESOURCE", True),
            ("Natural Resource", True),
            # Substring matches
            ("water resource extraction", True),
            ("natural resource extraction", True),
            ("economic activity", True),
            ("social aspect", True),
            # Slash-separated strings with resource
            ("resource/air", True),
            # String values that should return False
            ("emission", False),
            ("air", False),
            ("water", False),
            ("", False),
            ("emission/air", False),
        ],
    )
    def test_is_resource_with_string(self, value, expected):
        """Test is_resource with string values."""
        c = ContextField(value)
        assert (
            c.is_resource() is expected
        ), f"Expected is_resource() to be {expected} for {value!r}, but got {c.is_resource()}"

    @pytest.mark.parametrize(
        "value,expected",
        [
            # List values that should return True
            (["resource"], True),
            (["resources"], True),
            (["raw"], True),
            (["land use"], True),
            (["economic"], True),
            (["social"], True),
            (["raw materials"], True),
            (["RESOURCE"], True),  # Case insensitive
            (["emission", "resource", "air"], True),  # Multiple elements, one resource
            # List values that should return False
            (["emission", "air", "water"], False),
            ([], False),
        ],
    )
    def test_is_resource_with_list(self, value, expected):
        """Test is_resource with list values."""
        c = ContextField(value)
        assert (
            c.is_resource() is expected
        ), f"Expected is_resource() to be {expected} for {value!r}, but got {c.is_resource()}"

    @pytest.mark.parametrize(
        "value,expected",
        [
            # Tuple values that should return True
            (("resource",), True),
            (("raw",), True),
            (("emission", "resource", "air"), True),  # Multiple elements, one resource
            # Tuple values that should return False
            (("emission", "air"), False),
            ((), False),
        ],
    )
    def test_is_resource_with_tuple(self, value, expected):
        """Test is_resource with tuple values."""
        c = ContextField(value)
        assert (
            c.is_resource() is expected
        ), f"Expected is_resource() to be {expected} for {value!r}, but got {c.is_resource()}"
