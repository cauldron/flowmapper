import pytest

from flowmapper.context import MISSING_VALUES, ContextField


def test_context_uses_transformed():
    c = ContextField(
        original="Raw/(unspecified)",
        transformed=["Raw", "(unspecified)"],
    )
    assert c == ["Raw", "(unspecified)"], f"Expected c to equal ['Raw', '(unspecified)'], but got {c!r}"
    assert c.transformed == ["Raw", "(unspecified)"], f"Expected c.transformed to equal ['Raw', '(unspecified)'], but got {c.transformed!r}"


def test_context_transformed_from_tuple():
    c = ContextField(
        original="Raw/(unspecified)",
        transformed=("Raw", "(unspecified)"),
    )
    assert c == ["Raw", "(unspecified)"], f"Expected c to equal ['Raw', '(unspecified)'], but got {c!r}"
    assert c.transformed == ("Raw", "(unspecified)"), f"Expected c.transformed to equal ('Raw', '(unspecified)'), but got {c.transformed!r}"


def test_context_transformed_from_string_with_slash():
    c = ContextField(
        original="Raw/(unspecified)",
        transformed="Raw/(unspecified)",
    )
    assert c == ["Raw", "(unspecified)"], f"Expected c to equal ['Raw', '(unspecified)'], but got {c!r}"
    assert c.transformed == "Raw/(unspecified)", f"Expected c.transformed to equal 'Raw/(unspecified)', but got {c.transformed!r}"


def test_context_transformed_from_string():
    c = ContextField(
        original="Raw/(unspecified)",
        transformed="Raw",
    )
    assert c == ["Raw", "(unspecified)"], f"Expected c to equal ['Raw', '(unspecified)'], but got {c!r}"
    assert c.transformed == "Raw", f"Expected c.transformed to equal 'Raw', but got {c.transformed!r}"


def test_context_transformed_not_given():
    c = ContextField(
        original="Raw/(unspecified)",
    )
    assert c == ["Raw", "(unspecified)"], f"Expected c to equal ['Raw', '(unspecified)'], but got {c!r}"
    assert c.transformed == "Raw/(unspecified)", f"Expected c.transformed to equal 'Raw/(unspecified)', but got {c.transformed!r}"


def test_context_normalize_tuple():
    c = ContextField(
        original=("Raw",),
    )
    assert c.normalized == ("raw",), f"Expected c.normalized to equal ('raw',), but got {c.normalized!r}"


def test_context_normalize_string_with_slash():
    c = ContextField(
        original="A/B",
    )
    assert c.normalized == ("a", "b"), f"Expected c.normalized to equal ('a', 'b'), but got {c.normalized!r}"


def test_context_normalize_string():
    c = ContextField(
        original="A-B",
    )
    assert c.normalized == ("a-b",), f"Expected c.normalized to equal ('a-b',), but got {c.normalized!r}"


def test_context_normalize_error():
    class Foo:
        pass

    with pytest.raises(ValueError):
        ContextField(Foo())


def test_context_normalize_lowercase():
    c = ContextField(
        original="A-B",
    )
    assert c.normalized == ("a-b",), f"Expected c.normalized to equal ('a-b',), but got {c.normalized!r}"


def test_context_normalize_strip():
    c = ContextField(
        original=" A-B\t\n",
    )
    assert c.normalized == ("a-b",), f"Expected c.normalized to equal ('a-b',), but got {c.normalized!r}"


@pytest.mark.parametrize("string", MISSING_VALUES)
def test_context_missing_values(string):
    c = ContextField(
        original=("A", string),
    )
    assert c.original == ("A", string), f"Expected c.original to equal ('A', {string!r}), but got {c.original!r}"
    assert c.normalized == ("a",), f"Expected c.normalized to equal ('a',), but got {c.normalized!r}"


def test_context_generic_dunder():
    c = ContextField("A/B")
    assert repr(c) == "ContextField: 'A/B' -> '('a', 'b')'", f"Expected repr(c) to equal 'ContextField: 'A/B' -> '('a', 'b')'', but got {repr(c)!r}"
    assert repr(ContextField("")) == "ContextField: '' -> '()'", f"Expected repr(ContextField('')) to equal 'ContextField: '' -> '()'', but got {repr(ContextField(''))!r}"
    assert bool(c), f"Expected bool(c) to be True, but got {bool(c)}"
    assert isinstance(hash(c), int), f"Expected hash(c) to be an int, but got {type(hash(c))}"
    assert list(c) == ["a", "b"], f"Expected list(c) to equal ['a', 'b'], but got {list(c)!r}"


def test_context_in():
    a = ContextField("A")
    b = ContextField("A/B")
    assert b in a, "Expected b to be in a, but it was not"
    assert a not in b, "Expected a to not be in b, but it was"


def test_context_export_as_string():
    assert ContextField(["A", "B"]).export_as_string() == "A✂️B", f"Expected ContextField(['A', 'B']).export_as_string() to equal 'A✂️B', but got {ContextField(['A', 'B']).export_as_string()!r}"
    assert ContextField("A/B").export_as_string() == "A/B", f"Expected ContextField('A/B').export_as_string() to equal 'A/B', but got {ContextField('A/B').export_as_string()!r}"
    c = ContextField("A/B")
    c.original = {"A": "B"}
    with pytest.raises(ValueError):
        c.export_as_string()
