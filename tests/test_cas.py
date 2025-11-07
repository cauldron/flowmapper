import pytest

from flowmapper.cas import CASField


def test_cas_init():
    cas = CASField("0000096-49-1")
    assert cas.original == "0000096-49-1", f"Expected cas.original to be '0000096-49-1', but got {cas.original!r}"
    assert cas.transformed == "96-49-1", f"Expected cas.transformed to be '96-49-1', but got {cas.transformed!r}"
    assert cas.digits == (9, 6, 4, 9, 1), f"Expected cas.digits to be (9, 6, 4, 9, 1), but got {cas.digits!r}"


def test_cas_init_empty_string():
    cas = CASField("")
    assert cas.original == "", f"Expected cas.original to be '', but got {cas.original!r}"
    assert cas.transformed == "", f"Expected cas.transformed to be '', but got {cas.transformed!r}"
    assert cas.digits == (), f"Expected cas.digits to be (), but got {cas.digits!r}"


def test_cas_init_none():
    cas = CASField(None)
    assert cas.original is None, f"Expected cas.original to be None, but got {cas.original!r}"
    assert cas.transformed == "", f"Expected cas.transformed to be '', but got {cas.transformed!r}"
    assert cas.digits == (), f"Expected cas.digits to be (), but got {cas.digits!r}"


def test_cas_init_error():
    with pytest.raises(TypeError):
        CASField(96491)


def test_cas_export():
    assert CASField("7782-40-3").export == "7782-40-3", f"Expected CASField('7782-40-3').export to be '7782-40-3', but got {CASField('7782-40-3').export!r}"
    assert CASField("7782403").export == "7782-40-3", f"Expected CASField('7782403').export to be '7782-40-3', but got {CASField('7782403').export!r}"
    assert CASField("0007782403").export == "7782-40-3", f"Expected CASField('0007782403').export to be '7782-40-3', but got {CASField('0007782403').export!r}"
    assert CASField("").export == "", f"Expected CASField('').export to be '', but got {CASField('').export!r}"
    assert CASField(None).export == "", f"Expected CASField(None).export to be '', but got {CASField(None).export!r}"


def test_invalid_cas_check_digit():
    assert not CASField("96-49-2").valid, f"Expected CASField('96-49-2').valid to be False, but got {CASField('96-49-2').valid}"
    assert CASField("96-49-2").check_digit_expected == 1, f"Expected CASField('96-49-2').check_digit_expected to be 1, but got {CASField('96-49-2').check_digit_expected}"


def test_cas_repr():
    repr(CASField("0000096-49-1")) == "Valid CASField: '0000096-49-1' -> '96-49-1'"
    repr(CASField("0000096-49-2")) == "Invalid CASField: '0000096-49-2' -> '96-49-2'"
    repr(CASField("")) == "CASField with missing original value"


def test_equality_comparison():
    assert CASField("\t\n\n007440-05-3") == CASField("7440-05-3"), "Expected CASField('\\t\\n\\n007440-05-3') to equal CASField('7440-05-3'), but they are not equal"
    assert CASField("7440-05-3") == "0007440-05-3", "Expected CASField('7440-05-3') to equal '0007440-05-3', but they are not equal"
    assert CASField("7440-05-3") == "7440-05-3", "Expected CASField('7440-05-3') to equal '7440-05-3', but they are not equal"
    assert not CASField("7440-05-3") == "7782-40-3", "Expected CASField('7440-05-3') to not equal '7782-40-3', but they are equal"
    assert not CASField("7440-05-3") == CASField("7782-40-3"), "Expected CASField('7440-05-3') to not equal CASField('7782-40-3'), but they are equal"
    assert not CASField("") == CASField("7782-40-3"), "Expected CASField('') to not equal CASField('7782-40-3'), but they are equal"
    assert not CASField("7440-05-3") == CASField(""), "Expected CASField('7440-05-3') to not equal CASField(''), but they are equal"
    assert not CASField("") == CASField(""), "Expected CASField('') to not equal CASField(''), but they are equal"
    assert not CASField(None) == CASField(""), "Expected CASField(None) to not equal CASField(''), but they are equal"
    assert not CASField("") == CASField(None), "Expected CASField('') to not equal CASField(None), but they are equal"
