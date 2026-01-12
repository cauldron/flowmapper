import math

import pytest

from flowmapper.unit import UnitField


def test_equals_mass():
    u1 = UnitField("kg")
    u2 = UnitField("kilogram")

    assert (
        u1 == u2
    ), f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"


def test_energy():
    u1 = UnitField("kilowatt hour")
    u2 = UnitField("MJ")
    assert u1.compatible(
        u2
    ), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"
    assert (
        u1.conversion_factor(u2) == pytest.approx(3.6)
    ), f"Expected u1.conversion_factor(u2) to be 3.6, but got {u1.conversion_factor(u2)}"


def test_enrichment():
    u1 = UnitField("SWU")
    u2 = UnitField("tonne * SW")
    assert u1.compatible(
        u2
    ), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"
    assert (
        u1.conversion_factor(u2) == 1e-3
    ), f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_natural_gas():
    u1 = UnitField("nm3")
    u2 = UnitField("sm3")
    assert u1.compatible(
        u2
    ), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"


def test_livestock():
    u1 = UnitField("LU")
    u2 = UnitField("livestock unit")
    assert (
        u1.normalize() == u2.normalize()
    ), f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"


def test_freight():
    u1 = UnitField("kilogram * km")
    u2 = UnitField("tkm")
    assert (
        u1.conversion_factor(u2) == 1e-3
    ), f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_vehicular_travel():
    u1 = UnitField("vehicle * m")
    u2 = UnitField("vkm")
    assert (
        u1.conversion_factor(u2) == 1e-3
    ), f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


def test_person_travel():
    u1 = UnitField("person * m")
    u2 = UnitField("pkm")
    assert (
        u1.conversion_factor(u2) == 1e-3
    ), f"Expected u1.conversion_factor(u2) to be 1e-3, but got {u1.conversion_factor(u2)}"


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
    assert (
        u1.conversion_factor(u2) == 0.012
    ), f"Expected u1.conversion_factor(u2) to be 0.012, but got {u1.conversion_factor(u2)}"


class TestUnitFieldNormalize:
    """Test UnitField normalize method."""

    def test_normalize_with_valid_unit(self):
        """Test normalize with valid unit."""
        u = UnitField("kg")
        normalized = u.normalize()
        assert (
            normalized == "kilogram"
        ), f"Expected normalized to be 'kilogram', but got {normalized!r}"
        assert isinstance(
            normalized, UnitField
        ), f"Expected normalized to be a UnitField instance, but got {type(normalized)}"

    def test_normalize_with_mapped_unit(self):
        """Test normalize with unit that needs mapping."""
        # This tests the UNIT_MAPPING functionality
        u = UnitField("kilogram")
        normalized = u.normalize()
        # The unit should be normalized through UNIT_MAPPING if applicable
        assert isinstance(
            normalized, UnitField
        ), f"Expected normalized to be a UnitField instance, but got {type(normalized)}"

    def test_normalize_raises_error_undefined_unit(self):
        """Test normalize raises error for undefined unit."""
        u = UnitField("unknown_unit_xyz")
        with pytest.raises(ValueError, match="is unknown"):
            u.normalize()


class TestUnitFieldEq:
    """Test UnitField __eq__ method."""

    def test_eq_with_same_data(self):
        """Test equality with same data."""
        u1 = UnitField("kg")
        u2 = UnitField("kg")
        assert (
            u1 == u2
        ), f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"

    def test_eq_with_different_data_same_unit(self):
        """Test equality with different data but same unit (conversion_factor == 1)."""
        u1 = UnitField("kg")
        u2 = UnitField("kilogram")
        assert (
            u1 == u2
        ), f"Expected u1 to equal u2, but they are not equal (u1={u1!r}, u2={u2!r})"

    def test_eq_with_different_units(self):
        """Test equality with different units."""
        u1 = UnitField("kg")
        u2 = UnitField("g")
        assert (
            u1 != u2
        ), f"Expected u1 to not equal u2, but they are equal (u1={u1!r}, u2={u2!r})"

    def test_eq_with_string(self):
        """Test equality with string."""
        u = UnitField("kg")
        assert u == "kg", f"Expected u to equal 'kg', but they are not equal (u={u!r})"
        assert u != "g", f"Expected u to not equal 'g', but they are equal (u={u!r})"

    def test_eq_with_other_type(self):
        """Test equality with other types."""
        u = UnitField("kg")
        assert u != 123, f"Expected u to not equal 123, but they are equal (u={u!r})"
        assert u != None, f"Expected u to not equal None, but they are equal (u={u!r})"
        assert u != [], f"Expected u to not equal [], but they are equal (u={u!r})"


class TestUnitFieldCompatible:
    """Test UnitField compatible method."""

    def test_compatible_with_compatible_units(self):
        """Test compatible with compatible units."""
        u1 = UnitField("kg")
        u2 = UnitField("g")
        assert u1.compatible(
            u2
        ), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"

    def test_compatible_with_incompatible_units(self):
        """Test compatible with incompatible units."""
        u1 = UnitField("kg")
        u2 = UnitField("meter")
        assert not u1.compatible(
            u2
        ), f"Expected u1 to not be compatible with u2, but they are (u1={u1!r}, u2={u2!r})"

    def test_compatible_with_same_unit(self):
        """Test compatible with same unit."""
        u1 = UnitField("kg")
        u2 = UnitField("kg")
        assert u1.compatible(
            u2
        ), f"Expected u1 to be compatible with u2, but they are not (u1={u1!r}, u2={u2!r})"

    def test_compatible_with_non_unitfield(self):
        """Test compatible with non-UnitField type."""
        u1 = UnitField("kg")
        # Strings are now supported and work with compatible()
        assert u1.compatible(
            "kg"
        ), f"Expected u1 to be compatible with 'kg' string (strings are now supported), but it is not (u1={u1!r})"
        # Non-string, non-UnitField types should return False
        assert not u1.compatible(
            123
        ), f"Expected u1 to not be compatible with 123, but it is (u1={u1!r})"


class TestUnitFieldConversionFactor:
    """Test UnitField conversion_factor method."""

    def test_conversion_factor_with_same_data(self):
        """Test conversion_factor with same data."""
        u1 = UnitField("kg")
        u2 = UnitField("kg")
        result = u1.conversion_factor(u2)
        assert result == 1.0, f"Expected conversion_factor to be 1.0, but got {result}"

    def test_conversion_factor_with_non_unitfield(self):
        """Test conversion_factor with non-UnitField type."""
        u1 = UnitField("kg")
        # Strings are now supported and work with conversion_factor()
        result = u1.conversion_factor("kg")
        assert (
            result == 1.0
        ), f"Expected conversion_factor to be 1.0 for same unit string, but got {result}"
        # Non-string, non-UnitField types should return NaN
        result2 = u1.conversion_factor(123)
        assert math.isnan(
            result2
        ), f"Expected conversion_factor to be NaN for non-UnitField, non-string type, but got {result2}"

    def test_conversion_factor_with_undefined_unit(self):
        """Test conversion_factor with undefined unit."""
        u1 = UnitField("kg")
        u2 = UnitField("unknown_unit_xyz")
        result = u1.conversion_factor(u2)
        assert math.isnan(
            result
        ), f"Expected conversion_factor to be NaN for undefined unit, but got {result}"

    def test_conversion_factor_with_dimensionality_error(self):
        """Test conversion_factor with dimensionality error."""
        u1 = UnitField("kg")
        u2 = UnitField("meter")
        result = u1.conversion_factor(u2)
        assert math.isnan(
            result
        ), f"Expected conversion_factor to be NaN for incompatible units, but got {result}"

    def test_conversion_factor_zero_to_one(self):
        """Test conversion_factor from zero to one."""
        u1 = UnitField("mg")
        u2 = UnitField("kg")
        result = u1.conversion_factor(u2)
        assert (
            result == 1e-06
        ), f"Expected conversion_factor to be 1e-06, but got {result}"

    def test_conversion_factor_one_to_zero(self):
        """Test conversion_factor from one to zero."""
        u1 = UnitField("kg")
        u2 = UnitField("mg")
        result = u1.conversion_factor(u2)
        assert (
            result == 1e06
        ), f"Expected conversion_factor to be 1e06, but got {result}"
