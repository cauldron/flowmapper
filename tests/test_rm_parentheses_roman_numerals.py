from flowmapper.utils import (
    rm_parentheses_roman_numerals,
    rm_roman_numerals_ionic_state,
)


def test_rm_parentheses_roman_numerals():
    assert rm_parentheses_roman_numerals("chromium (iii)") == "chromium iii", f"Expected rm_parentheses_roman_numerals('chromium (iii)') to equal 'chromium iii', but got {rm_parentheses_roman_numerals('chromium (iii)')!r}"
    assert rm_parentheses_roman_numerals("chromium ( iii )") == "chromium iii", f"Expected rm_parentheses_roman_numerals('chromium ( iii )') to equal 'chromium iii', but got {rm_parentheses_roman_numerals('chromium ( iii )')!r}"
    actual = rm_parentheses_roman_numerals("water (evapotranspiration)")
    assert (
        actual
        == "water (evapotranspiration)"
    ), f"Expected rm_parentheses_roman_numerals('water (evapotranspiration)') to equal 'water (evapotranspiration)', but got {actual!r}"
    assert rm_parentheses_roman_numerals("metolachlor, (s)") == "metolachlor, (s)", f"Expected rm_parentheses_roman_numerals('metolachlor, (s)') to equal 'metolachlor, (s)', but got {rm_parentheses_roman_numerals('metolachlor, (s)')!r}"
    assert rm_parentheses_roman_numerals("chromium (vi)") == "chromium vi", f"Expected rm_parentheses_roman_numerals('chromium (vi)') to equal 'chromium vi', but got {rm_parentheses_roman_numerals('chromium (vi)')!r}"
    assert rm_parentheses_roman_numerals("beryllium (ii)") == "beryllium ii", f"Expected rm_parentheses_roman_numerals('beryllium (ii)') to equal 'beryllium ii', but got {rm_parentheses_roman_numerals('beryllium (ii)')!r}"
    assert rm_parentheses_roman_numerals("thallium (i)") == "thallium i", f"Expected rm_parentheses_roman_numerals('thallium (i)') to equal 'thallium i', but got {rm_parentheses_roman_numerals('thallium (i)')!r}"
    assert rm_parentheses_roman_numerals("tin (iv) oxide") == "tin iv oxide", f"Expected rm_parentheses_roman_numerals('tin (iv) oxide') to equal 'tin iv oxide', but got {rm_parentheses_roman_numerals('tin (iv) oxide')!r}"
    # Test uppercase roman numerals
    assert rm_parentheses_roman_numerals("Iron (II)") == "Iron II", f"Expected rm_parentheses_roman_numerals('Iron (II)') to equal 'Iron II', but got {rm_parentheses_roman_numerals('Iron (II)')!r}"
    assert rm_parentheses_roman_numerals("Iron ( II )") == "Iron II", f"Expected rm_parentheses_roman_numerals('Iron ( II )') to equal 'Iron II', but got {rm_parentheses_roman_numerals('Iron ( II )')!r}"
    assert rm_parentheses_roman_numerals("Chromium (III)") == "Chromium III", f"Expected rm_parentheses_roman_numerals('Chromium (III)') to equal 'Chromium III', but got {rm_parentheses_roman_numerals('Chromium (III)')!r}"
    assert rm_parentheses_roman_numerals("Mercury (IV)") == "Mercury IV", f"Expected rm_parentheses_roman_numerals('Mercury (IV)') to equal 'Mercury IV', but got {rm_parentheses_roman_numerals('Mercury (IV)')!r}"
    assert rm_parentheses_roman_numerals("Manganese (VI)") == "Manganese VI", f"Expected rm_parentheses_roman_numerals('Manganese (VI)') to equal 'Manganese VI', but got {rm_parentheses_roman_numerals('Manganese (VI)')!r}"


def test_rm_roman_numerals_ionic_state():
    assert rm_roman_numerals_ionic_state("mercury (ii)") == "mercury", f"Expected rm_roman_numerals_ionic_state('mercury (ii)') to equal 'mercury', but got {rm_roman_numerals_ionic_state('mercury (ii)')!r}"
    assert rm_roman_numerals_ionic_state("manganese (ii)") == "manganese", f"Expected rm_roman_numerals_ionic_state('manganese (ii)') to equal 'manganese', but got {rm_roman_numerals_ionic_state('manganese (ii)')!r}"
    assert rm_roman_numerals_ionic_state("molybdenum (vi)") == "molybdenum", f"Expected rm_roman_numerals_ionic_state('molybdenum (vi)') to equal 'molybdenum', but got {rm_roman_numerals_ionic_state('molybdenum (vi)')!r}"
