from flowmapper.fields import StringField


def test_string_field_empty():
    sf = StringField(None)
    assert (
        sf.original is None
    ), f"Expected sf.original to be None, but got {sf.original!r}"
    assert (
        sf.normalized == ""
    ), f"Expected sf.normalized to be '', but got {sf.normalized!r}"
    assert sf != "", "Expected sf to not equal '', but they are equal"
    assert sf != "a", "Expected sf to not equal 'a', but they are equal"
    assert sf != StringField(
        "a"
    ), "Expected sf to not equal StringField('a'), but they are equal"
    assert sf is not None, "Expected sf to not be None, but it was None"
    assert not sf, f"Expected sf to be falsy, but got {sf}"
    assert (
        repr(sf) == "StringField with missing original value"
    ), f"Expected repr(sf) to equal 'StringField with missing original value', but got {repr(sf)!r}"


def test_string_field_no_transformed():
    sf = StringField("A", use_lowercase=False)
    assert (
        sf.original == "A"
    ), f"Expected sf.original to be 'A', but got {sf.original!r}"
    assert (
        sf.normalized == "A"
    ), f"Expected sf.normalized to be 'A', but got {sf.normalized!r}"
    assert sf == "A", "Expected sf to equal 'A', but they are not equal"
    assert sf != "a", "Expected sf to not equal 'a', but they are equal"
    assert sf == StringField(
        "A", use_lowercase=True
    ), "Expected sf to equal StringField('A', use_lowercase=True), but they are not equal"
    assert sf == StringField(
        "A", use_lowercase=False
    ), "Expected sf to equal StringField('A', use_lowercase=False), but they are not equal"
    assert sf != "B", "Expected sf to not equal 'B', but they are equal"
    assert (
        not sf.use_lowercase
    ), f"Expected sf.use_lowercase to be False, but got {sf.use_lowercase}"
    assert sf, f"Expected sf to be truthy, but got {sf}"
    assert (
        repr(sf) == "StringField: 'A' -> 'A'"
    ), f"Expected repr(sf) to equal 'StringField: 'A' -> 'A'', but got {repr(sf)!r}"


def test_string_field_no_transformed_lowercase():
    sf = StringField("A", use_lowercase=True)
    assert (
        sf.original == "A"
    ), f"Expected sf.original to be 'A', but got {sf.original!r}"
    assert (
        sf.normalized == "a"
    ), f"Expected sf.normalized to be 'a', but got {sf.normalized!r}"
    assert sf == "a", "Expected sf to equal 'a', but they are not equal"
    assert sf == "A", "Expected sf to equal 'A', but they are not equal"
    assert sf == StringField(
        "A", use_lowercase=True
    ), "Expected sf to equal StringField('A', use_lowercase=True), but they are not equal"
    assert sf == StringField(
        "A", use_lowercase=False
    ), "Expected sf to equal StringField('A', use_lowercase=False), but they are not equal"
    assert sf != "B", "Expected sf to not equal 'B', but they are equal"
    assert (
        sf.use_lowercase
    ), f"Expected sf.use_lowercase to be True, but got {sf.use_lowercase}"
    assert sf, f"Expected sf to be truthy, but got {sf}"
    assert (
        repr(sf) == "StringField: 'A' -> 'a'"
    ), f"Expected repr(sf) to equal 'StringField: 'A' -> 'a'', but got {repr(sf)!r}"


def test_string_field_transformed():
    sf = StringField("A*", use_lowercase=False)
    assert (
        sf.original == "A*"
    ), f"Expected sf.original to be 'A*', but got {sf.original!r}"
    assert (
        sf.normalized == "A*"
    ), f"Expected sf.normalized to be 'A*', but got {sf.normalized!r}"
    assert sf != "A", "Expected sf to not equal 'A', but they are equal"
    assert sf != "a*", "Expected sf to not equal 'a*', but they are equal"
    assert sf == "A*", "Expected sf to equal 'A*', but they are not equal"
    assert sf == StringField(
        "A*", use_lowercase=True
    ), "Expected sf to equal StringField('A*', use_lowercase=True), but they are not equal"
    assert sf == StringField(
        "A*", use_lowercase=False
    ), "Expected sf to equal StringField('A*', use_lowercase=False), but they are not equal"
    assert sf != "B", "Expected sf to not equal 'B', but they are equal"
    assert (
        not sf.use_lowercase
    ), f"Expected sf.use_lowercase to be False, but got {sf.use_lowercase}"
    assert sf, f"Expected sf to be truthy, but got {sf}"
    assert (
        repr(sf) == "StringField: 'A*' -> 'A*'"
    ), f"Expected repr(sf) to equal 'StringField: 'A*' -> 'A*'', but got {repr(sf)!r}"


def test_string_field_transformed_lowercase():
    sf = StringField("A*", use_lowercase=True)
    assert (
        sf.original == "A*"
    ), f"Expected sf.original to be 'A*', but got {sf.original!r}"
    assert (
        sf.normalized == "a*"
    ), f"Expected sf.normalized to be 'a*', but got {sf.normalized!r}"
    assert sf == "a*", "Expected sf to equal 'a*', but they are not equal"
    assert sf == "A*", "Expected sf to equal 'A*', but they are not equal"
    assert sf == StringField(
        "A*", use_lowercase=True
    ), "Expected sf to equal StringField('A*', use_lowercase=True), but they are not equal"
    assert sf == StringField(
        "A*", use_lowercase=False
    ), "Expected sf to equal StringField('A*', use_lowercase=False), but they are not equal"
    assert sf != "B", "Expected sf to not equal 'B', but they are equal"
    assert (
        sf.use_lowercase
    ), f"Expected sf.use_lowercase to be True, but got {sf.use_lowercase}"
    assert sf, f"Expected sf to be truthy, but got {sf}"
    assert (
        repr(sf) == "StringField: 'A*' -> 'a*'"
    ), f"Expected repr(sf) to equal 'StringField: 'A*' -> 'a*'', but got {repr(sf)!r}"
