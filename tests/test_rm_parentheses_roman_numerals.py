from flowmapper.utils import (
    rm_parentheses_roman_numerals,
    rm_roman_numerals_ionic_state,
)


def test_rm_parentheses_roman_numerals():
    assert rm_parentheses_roman_numerals("chromium (iii)") == "chromium iii"
    assert rm_parentheses_roman_numerals("chromium ( iii )") == "chromium iii"
    assert (
        rm_parentheses_roman_numerals("water (evapotranspiration)")
        == "water (evapotranspiration)"
    )
    assert rm_parentheses_roman_numerals("metolachlor, (s)") == "metolachlor, (s)"
    assert rm_parentheses_roman_numerals("chromium (vi)") == "chromium vi"
    assert rm_parentheses_roman_numerals("beryllium (ii)") == "beryllium ii"
    assert rm_parentheses_roman_numerals("thallium (i)") == "thallium i"
    assert rm_parentheses_roman_numerals("tin (iv) oxide") == "tin iv oxide"
    # Test uppercase roman numerals
    assert rm_parentheses_roman_numerals("Iron (II)") == "Iron II"
    assert rm_parentheses_roman_numerals("Iron ( II )") == "Iron II"
    assert rm_parentheses_roman_numerals("Chromium (III)") == "Chromium III"
    assert rm_parentheses_roman_numerals("Mercury (IV)") == "Mercury IV"
    assert rm_parentheses_roman_numerals("Manganese (VI)") == "Manganese VI"


def test_rm_roman_numerals_ionic_state():
    assert rm_roman_numerals_ionic_state("mercury (ii)") == "mercury"
    assert rm_roman_numerals_ionic_state("manganese (ii)") == "manganese"
    assert rm_roman_numerals_ionic_state("molybdenum (vi)") == "molybdenum"
