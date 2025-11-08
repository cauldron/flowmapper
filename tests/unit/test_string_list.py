"""Unit tests for StringList class."""

import pytest

from flowmapper.string_list import StringList
from flowmapper.string_field import StringField


class TestStringListInitialization:
    """Test StringList initialization."""

    def test_init_with_string_list(self):
        """Test initialization with a list of strings."""
        sl = StringList(["a", "b", "c"])
        assert len(sl) == 3, f"Expected len(sl) to be 3, but got {len(sl)}"
        assert len(sl.strings) == 3, f"Expected len(sl.strings) to be 3, but got {len(sl.strings)}"

    def test_init_with_empty_list(self):
        """Test initialization with empty list."""
        sl = StringList([])
        assert len(sl) == 0, f"Expected len(sl) to be 0, but got {len(sl)}"
        assert len(sl.strings) == 0, f"Expected len(sl.strings) to be 0, but got {len(sl.strings)}"

    def test_init_with_stringfield_list(self):
        """Test initialization with a list of StringField objects."""
        sf1 = StringField("a")
        sf2 = StringField("b")
        sl = StringList([sf1, sf2])
        assert len(sl) == 2, f"Expected len(sl) to be 2, but got {len(sl)}"
        assert sl.strings[0] is sf1, f"Expected sl.strings[0] to be the same StringField instance, but it is not"
        assert sl.strings[1] is sf2, f"Expected sl.strings[1] to be the same StringField instance, but it is not"

    def test_init_with_mixed_list(self):
        """Test initialization with a mix of strings and StringField objects."""
        sf1 = StringField("a")
        sl = StringList([sf1, "b", "c"])
        assert len(sl) == 3, f"Expected len(sl) to be 3, but got {len(sl)}"
        assert sl.strings[0] is sf1, f"Expected sl.strings[0] to be the same StringField instance, but it is not"
        assert isinstance(sl.strings[1], StringField), f"Expected sl.strings[1] to be a StringField instance, but got {type(sl.strings[1])}"
        assert isinstance(sl.strings[2], StringField), f"Expected sl.strings[2] to be a StringField instance, but got {type(sl.strings[2])}"

    def test_init_converts_strings_to_stringfields(self):
        """Test that initialization converts strings to StringField objects."""
        sl = StringList(["test"])
        assert isinstance(sl.strings[0], StringField), f"Expected sl.strings[0] to be a StringField instance, but got {type(sl.strings[0])}"
        assert sl.strings[0].value == "test", f"Expected sl.strings[0].value to be 'test', but got {sl.strings[0].value!r}"


class TestStringListContains:
    """Test StringList __contains__ method."""

    def test_contains_with_string(self):
        """Test __contains__ with a string."""
        sl = StringList(["a", "b", "c"])
        assert "a" in sl, f"Expected 'a' to be in sl, but it is not"
        assert "b" in sl, f"Expected 'b' to be in sl, but it is not"
        assert "c" in sl, f"Expected 'c' to be in sl, but it is not"
        assert "d" not in sl, f"Expected 'd' to not be in sl, but it is"

    def test_contains_with_stringfield(self):
        """Test __contains__ with a StringField."""
        sl = StringList(["a", "b", "c"])
        assert StringField("a") in sl, f"Expected StringField('a') to be in sl, but it is not"
        assert StringField("d") not in sl, f"Expected StringField('d') to not be in sl, but it is"

    def test_contains_with_empty_list(self):
        """Test __contains__ with empty list."""
        sl = StringList([])
        assert "a" not in sl, f"Expected 'a' to not be in empty sl, but it is"

    def test_contains_case_insensitive(self):
        """Test __contains__ with case-insensitive matching."""
        sl = StringList(["Test", "Value"])
        assert "test" in sl, f"Expected 'test' to be in sl (case-insensitive), but it is not"
        assert "TEST" in sl, f"Expected 'TEST' to be in sl (case-insensitive), but it is not"
        assert "value" in sl, f"Expected 'value' to be in sl (case-insensitive), but it is not"


class TestStringListIter:
    """Test StringList __iter__ method."""

    def test_iter_yields_stringfields(self):
        """Test that __iter__ yields StringField objects."""
        sl = StringList(["a", "b", "c"])
        items = list(sl)
        assert len(items) == 3, f"Expected iter to yield 3 items, but got {len(items)}"
        assert all(isinstance(item, StringField) for item in items), f"Expected all items to be StringField instances, but they are not"

    def test_iter_with_empty_list(self):
        """Test __iter__ with empty list."""
        sl = StringList([])
        items = list(sl)
        assert len(items) == 0, f"Expected iter to yield 0 items, but got {len(items)}"

    def test_iter_order(self):
        """Test that __iter__ maintains order."""
        sl = StringList(["first", "second", "third"])
        items = [item.value for item in sl]
        assert items == ["first", "second", "third"], f"Expected items to be ['first', 'second', 'third'], but got {items}"


class TestStringListLen:
    """Test StringList __len__ method."""

    def test_len_with_items(self):
        """Test __len__ with items."""
        sl = StringList(["a", "b", "c"])
        assert len(sl) == 3, f"Expected len(sl) to be 3, but got {len(sl)}"

    def test_len_with_empty_list(self):
        """Test __len__ with empty list."""
        sl = StringList([])
        assert len(sl) == 0, f"Expected len(sl) to be 0, but got {len(sl)}"

    def test_len_with_single_item(self):
        """Test __len__ with single item."""
        sl = StringList(["single"])
        assert len(sl) == 1, f"Expected len(sl) to be 1, but got {len(sl)}"


class TestStringListBool:
    """Test StringList __bool__ method."""

    def test_bool_with_items(self):
        """Test __bool__ with items."""
        sl = StringList(["a", "b"])
        assert bool(sl) is True, f"Expected bool(sl) to be True, but got {bool(sl)}"

    def test_bool_with_empty_list(self):
        """Test __bool__ with empty list."""
        sl = StringList([])
        assert bool(sl) is False, f"Expected bool(sl) to be False, but got {bool(sl)}"

    def test_bool_with_none_original(self):
        """Test __bool__ with None original."""
        sl = StringList(None)
        assert bool(sl) is False, f"Expected bool(sl) to be False when original is None, but got {bool(sl)}"


class TestStringListRepr:
    """Test StringList __repr__ method."""

    def test_repr_with_items(self):
        """Test __repr__ with items."""
        sl = StringList(["a", "b"])
        repr_str = repr(sl)
        assert "StringList:" in repr_str, f"Expected repr to contain 'StringList:', but got {repr_str!r}"
        assert "a" in repr_str or "StringField" in repr_str, f"Expected repr to contain item representation, but got {repr_str!r}"

    def test_repr_with_empty_list(self):
        """Test __repr__ with empty list."""
        sl = StringList([])
        expected = "StringList: Empty"
        assert repr(sl) == expected, f"Expected repr(sl) to be {expected!r}, but got {repr(sl)!r}"

    def test_repr_with_none_original(self):
        """Test __repr__ with None original."""
        sl = StringList(None)
        expected = "StringList: Empty"
        assert repr(sl) == expected, f"Expected repr(sl) to be {expected!r}, but got {repr(sl)!r}"

    def test_repr_with_single_item(self):
        """Test __repr__ with single item."""
        sl = StringList(["test"])
        repr_str = repr(sl)
        assert "StringList:" in repr_str, f"Expected repr to contain 'StringList:', but got {repr_str!r}"
        assert repr_str != "StringList: Empty", f"Expected repr to not be 'StringList: Empty' for non-empty list, but got {repr_str!r}"


class TestStringListEdgeCases:
    """Test StringList edge cases."""

    def test_empty_strings_in_list(self):
        """Test initialization with empty strings in list."""
        sl = StringList(["", "a", ""])
        assert len(sl) == 3, f"Expected len(sl) to be 3, but got {len(sl)}"
        assert sl.strings[0].value == "", f"Expected sl.strings[0].value to be '', but got {sl.strings[0].value!r}"
        assert sl.strings[1].value == "a", f"Expected sl.strings[1].value to be 'a', but got {sl.strings[1].value!r}"

    def test_whitespace_in_list(self):
        """Test initialization with whitespace in list."""
        sl = StringList(["  a  ", "  b  "])
        assert len(sl) == 2, f"Expected len(sl) to be 2, but got {len(sl)}"
        assert sl.strings[0].value == "  a  ", f"Expected sl.strings[0].value to preserve whitespace, but got {sl.strings[0].value!r}"

    def test_contains_with_empty_string(self):
        """Test __contains__ with empty string."""
        sl = StringList(["", "a"])
        assert "" in sl, f"Expected '' to be in sl, but it is not"
        assert "a" in sl, f"Expected 'a' to be in sl, but it is not"

    def test_iteration_preserves_order(self):
        """Test that iteration preserves the order of items."""
        original = ["z", "a", "m"]
        sl = StringList(original)
        values = [item.value for item in sl]
        assert values == original, f"Expected values to match original order {original}, but got {values}"

    def test_stringfield_instances_preserved(self):
        """Test that StringField instances are preserved, not recreated."""
        sf1 = StringField("a")
        sf2 = StringField("b")
        sl = StringList([sf1, sf2, "c"])
        assert sl.strings[0] is sf1, f"Expected sl.strings[0] to be the same instance as sf1, but it is not"
        assert sl.strings[1] is sf2, f"Expected sl.strings[1] to be the same instance as sf2, but it is not"
        assert sl.strings[2] is not sf1, f"Expected sl.strings[2] to be a different instance, but it is the same"
        assert isinstance(sl.strings[2], StringField), f"Expected sl.strings[2] to be a StringField instance, but got {type(sl.strings[2])}"

    def test_single_item_list(self):
        """Test initialization with single item."""
        sl = StringList(["single"])
        assert len(sl) == 1, f"Expected len(sl) to be 1, but got {len(sl)}"
        assert sl.strings[0].value == "single", f"Expected sl.strings[0].value to be 'single', but got {sl.strings[0].value!r}"

    def test_unicode_strings(self):
        """Test initialization with unicode strings."""
        sl = StringList(["café", "naïve"])
        assert len(sl) == 2, f"Expected len(sl) to be 2, but got {len(sl)}"
        assert sl.strings[0].value == "café", f"Expected sl.strings[0].value to be 'café', but got {sl.strings[0].value!r}"
        assert sl.strings[1].value == "naïve", f"Expected sl.strings[1].value to be 'naïve', but got {sl.strings[1].value!r}"

