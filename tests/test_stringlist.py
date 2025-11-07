from flowmapper.string_list import StringList


def test_string_list_empty():
    sl = StringList([])
    assert sl.data == [], f"Expected sl.data to be [], but got {sl.data}"
    assert list(iter(sl)) == [], f"Expected list(iter(sl)) to be [], but got {list(iter(sl))}"
    assert len(sl) == 0, f"Expected len(sl) to be 0, but got {len(sl)}"
    assert not sl, f"Expected sl to be falsy, but got {sl}"
    assert repr(sl) == "StringList: Empty", f"Expected repr(sl) to equal 'StringList: Empty', but got {repr(sl)!r}"
    assert 1 not in sl, "Expected 1 to not be in sl, but it was"


def test_string_list_no_transformed():
    sl = StringList(["A", "b"])
    assert "A" in sl, "Expected 'A' to be in sl, but it was not"
    assert "b" in sl, "Expected 'b' to be in sl, but it was not"
    assert len(sl) == 2, f"Expected len(sl) to be 2, but got {len(sl)}"
    assert sl, f"Expected sl to be truthy, but got {sl}"
    expected_repr = "StringList: [\"StringField: 'A' -> 'a'\", \"StringField: 'b' -> 'b'\"]"
    assert (
        repr(sl)
        == expected_repr
    ), f"Expected repr(sl) to equal {expected_repr!r}, but got {repr(sl)!r}"
    assert list(iter(sl)) == ["a", "b"], f"Expected list(iter(sl)) to equal ['a', 'b'], but got {list(iter(sl))}"
    assert sl.data[0].original == "A", f"Expected sl.data[0].original to be 'A', but got {sl.data[0].original!r}"
    assert sl.data[0].normalized == "a", f"Expected sl.data[0].normalized to be 'a', but got {sl.data[0].normalized!r}"


def test_string_list_transformed():
    sl = StringList(["A", "b"], ["A*", "b"])
    assert "A*" in sl, "Expected 'A*' to be in sl, but it was not"
    assert "b" in sl, "Expected 'b' to be in sl, but it was not"
    assert len(sl) == 2, f"Expected len(sl) to be 2, but got {len(sl)}"
    assert sl, f"Expected sl to be truthy, but got {sl}"
    expected_repr = "StringList: [\"StringField: 'A' -> 'a*'\", \"StringField: 'b' -> 'b'\"]"
    assert (
        repr(sl)
        == expected_repr
    ), f"Expected repr(sl) to equal {expected_repr!r}, but got {repr(sl)!r}"
    assert list(iter(sl)) == ["a*", "b"], f"Expected list(iter(sl)) to equal ['a*', 'b'], but got {list(iter(sl))}"
    assert sl.data[0].original == "A", f"Expected sl.data[0].original to be 'A', but got {sl.data[0].original!r}"
    assert sl.data[0].normalized == "a*", f"Expected sl.data[0].normalized to be 'a*', but got {sl.data[0].normalized!r}"
