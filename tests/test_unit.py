import math

from flowmapper.transformation_mapping import prepare_transformations
from flowmapper.unit import UnitField
from flowmapper.utils import apply_transformations, load_standard_transformations


def test_equals_with_loaded_transformation():
    transformations = prepare_transformations(load_standard_transformations())

    a = {"unit": "M2A"}
    a_t = apply_transformations(a, transformations)
    b = {"unit": "m2*year"}
    b_t = apply_transformations(b, transformations)

    u1 = UnitField(a["unit"], a_t["unit"])
    u2 = UnitField(b["unit"], b_t["unit"])

    assert u1 == u2, f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"


def test_equals_mass():
    u1 = UnitField("kg")
    u2 = UnitField("kilogram")

    assert u1 == u2, f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"


def test_energy():
    u1 = UnitField("kilowatt hour")
    u2 = UnitField("MJ")
    assert u1.compatible(u2), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"
    assert u1.conversion_factor(u2) == 3.6, f"Expected u1.conversion_factor(u2) to be 3.6, but got {u1.conversion_factor(u2)}"


def test_enrichment():
    u1 = UnitField("SWU")
    u2 = UnitField("tonne * SW")
    assert u1.compatible(u2), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"
    assert u1.conversion_factor(u2) == 1e-3, f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_natural_gas():
    u1 = UnitField("nm3")
    u2 = UnitField("sm3")
    assert u1.compatible(u2), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"


def test_livestock():
    u1 = UnitField("LU")
    u2 = UnitField("livestock unit")
    assert u1 == u2, f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"


def test_freight():
    u1 = UnitField("kilogram * km")
    u2 = UnitField("tkm")
    assert u1.conversion_factor(u2) == 1e-3, f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_vehicular_travel():
    u1 = UnitField("vehicle * m")
    u2 = UnitField("vkm")
    assert u1.conversion_factor(u2) == 1e-3, f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_person_travel():
    u1 = UnitField("person * m")
    u2 = UnitField("pkm")
    assert u1.conversion_factor(u2) == 1e-3, f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_conversion_factor():
    u1 = UnitField("mg")
    u2 = UnitField("kg")
    actual = u1.conversion_factor(u2)
    assert actual == 1e-06, f"Expected actual to be 1e-06, but got {actual}"


def test_nan_conversion_factor():
    u1 = UnitField("bq")
    u2 = UnitField("kg")
    actual = u1.conversion_factor(u2)
    assert math.isnan(actual), f"Expected actual to be NaN, but got {actual}"


def test_complex_conversions():
    u1 = UnitField("square_meter_year / t")
    u2 = UnitField("(meter ** 2 * month) / kg")
    assert u1.conversion_factor(u2) == 0.012, f"Expected u1.conversion_factor(u2) to be 0.012, but got {u1.conversion_factor(u2)}"
