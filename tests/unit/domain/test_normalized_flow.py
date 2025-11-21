"""Unit tests for NormalizedFlow class."""

from copy import copy

import pytest

from flowmapper.domain.flow import Flow
from flowmapper.domain.normalized_flow import NormalizedFlow


class TestNormalizedFlowResetCurrent:
    """Test NormalizedFlow reset_current method."""

    def test_reset_current_resets_to_normalized(self):
        """Test reset_current resets current to normalized flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify current
        nf.update_current(name="Modified name")
        assert (
            nf.current.name.data != normalized.name.data
        ), "Expected current to be different from normalized after update"

        # Reset
        nf.reset_current()
        assert (
            nf.current.name.data == normalized.name.data
        ), f"Expected current.name to equal normalized.name after reset, but got {nf.current.name.data!r} != {normalized.name.data!r}"
        assert (
            nf.current.unit.data == normalized.unit.data
        ), f"Expected current.unit to equal normalized.unit after reset, but got {nf.current.unit.data!r} != {normalized.unit.data!r}"
        assert (
            nf.current.context.value == normalized.context.value
        ), f"Expected current.context to equal normalized.context after reset, but got {nf.current.context.value!r} != {normalized.context.value!r}"

    def test_reset_current_creates_new_instance(self):
        """Test reset_current creates a new Flow instance."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify current
        nf.update_current(name="Modified name")
        old_current_id = nf.current._id

        # Reset
        nf.reset_current()
        assert (
            nf.current._id != old_current_id
        ), "Expected reset_current to create a new Flow instance with different _id"
        assert (
            nf.current is not normalized
        ), "Expected reset_current to create a copy, not reference to normalized"

    def test_reset_current_preserves_normalized(self):
        """Test reset_current does not modify normalized flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify current multiple times
        nf.update_current(name="First modification")
        nf.update_current(name="Second modification")
        nf.update_current(unit="g")

        # Reset
        nf.reset_current()

        # Check normalized is unchanged
        assert (
            normalized.name.data == "carbon dioxide"
        ), f"Expected normalized.name to be unchanged, but got {normalized.name.data!r}"
        # Unit is normalized (kg -> kilogram), so check normalized value
        assert (
            normalized.unit.data == "kilogram"
        ), f"Expected normalized.unit to be unchanged, but got {normalized.unit.data!r}"

    def test_reset_current_with_complex_flow(self):
        """Test reset_current with flow containing all fields."""
        data = {
            "name": "Carbon dioxide, in air",
            "context": ["Raw", "(unspecified)"],
            "unit": "kg",
            "identifier": "test-id-123",
            "location": "US",
            "cas_number": "000124-38-9",
            "synonyms": ["CO2"],
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify multiple fields
        nf.update_current(name="Modified", unit="g", location="CA")

        # Reset
        nf.reset_current()

        # Verify all fields are reset
        assert (
            nf.current.name.data == normalized.name.data
        ), "Expected name to be reset to normalized"
        assert (
            nf.current.unit.data == normalized.unit.data
        ), "Expected unit to be reset to normalized"
        assert (
            nf.current.location == normalized.location
        ), "Expected location to be reset to normalized"
        assert (
            nf.current.identifier == normalized.identifier
        ), "Expected identifier to be reset to normalized"
        assert (
            nf.current.cas_number == normalized.cas_number
        ), "Expected cas_number to be reset to normalized"


class TestNormalizedFlowUpdateCurrent:
    """Test NormalizedFlow update_current method."""

    def test_update_current_with_name(self):
        """Test update_current with name parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(name="Updated name")
        assert (
            nf.current.name.data == "Updated name"
        ), f"Expected current.name to be 'Updated name', but got {nf.current.name.data!r}"
        assert (
            nf.current.unit.data == normalized.unit.data
        ), "Expected unit to remain unchanged"
        assert (
            nf.current.context.value == normalized.context.value
        ), "Expected context to remain unchanged"

    def test_update_current_with_unit(self):
        """Test update_current with unit parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(unit="g")
        assert (
            nf.current.unit.data == "g"
        ), f"Expected current.unit to be 'g', but got {nf.current.unit.data!r}"
        assert (
            nf.current.name.data == normalized.name.data
        ), "Expected name to remain unchanged"

    def test_update_current_with_context(self):
        """Test update_current with context parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(context=["water", "unspecified"])
        assert nf.current.context.value == [
            "water",
            "unspecified",
        ], f"Expected current.context to be ['water', 'unspecified'], but got {nf.current.context.value!r}"

    def test_update_current_with_multiple_fields(self):
        """Test update_current with multiple fields."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(name="Updated name", unit="g", context="water")
        assert nf.current.name.data == "Updated name", "Expected name to be updated"
        assert nf.current.unit.data == "g", "Expected unit to be updated"
        assert nf.current.context.value == "water", "Expected context to be updated"

    def test_update_current_with_location(self):
        """Test update_current with location parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "location": "US",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(location="CA")
        assert (
            nf.current.location == "CA"
        ), f"Expected current.location to be 'CA', but got {nf.current.location!r}"

    def test_update_current_with_identifier(self):
        """Test update_current with identifier parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "original-id",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(identifier="new-id")
        assert (
            nf.current.identifier == "new-id"
        ), f"Expected current.identifier to be 'new-id', but got {nf.current.identifier!r}"

    def test_update_current_with_cas_number(self):
        """Test update_current with cas_number parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "cas_number": "000124-38-9",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(cas_number="000078-79-5")
        # CAS numbers are normalized (leading zeros removed) when passed through from_string
        assert (
            nf.current.cas_number.data == "78-79-5"
        ), f"Expected current.cas_number to be '78-79-5' (normalized), but got {nf.current.cas_number.data!r}"

    def test_update_current_with_synonyms(self):
        """Test update_current with synonyms parameter."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "synonyms": ["CO2"],
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(synonyms=["CO2", "carbon dioxide"])
        assert nf.current.synonyms == [
            "CO2",
            "carbon dioxide",
        ], f"Expected current.synonyms to be ['CO2', 'carbon dioxide'], but got {nf.current.synonyms!r}"

    def test_update_current_creates_new_instance(self):
        """Test update_current creates a new Flow instance."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        old_current_id = nf.current._id
        nf.update_current(name="Updated")
        assert (
            nf.current._id != old_current_id
        ), "Expected update_current to create a new Flow instance with different _id"

    def test_update_current_preserves_normalized(self):
        """Test update_current does not modify normalized flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(name="Updated", unit="g")
        assert (
            normalized.name.data == "carbon dioxide"
        ), "Expected normalized.name to be unchanged"
        # Unit is normalized (kg -> kilogram), so check normalized value
        assert (
            normalized.unit.data == "kilogram"
        ), f"Expected normalized.unit to be unchanged, but got {normalized.unit.data!r}"

    def test_update_current_based_on_normalized(self):
        """Test update_current uses normalized as base, not current."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # First update
        nf.update_current(name="First update")
        assert nf.current.name.data == "First update", "Expected first update to work"

        # Second update - should be based on normalized, not "First update"
        nf.update_current(unit="g")
        assert (
            nf.current.name.data == normalized.name.data
        ), "Expected name to revert to normalized value when not specified in update"
        assert nf.current.unit.data == "g", "Expected unit to be updated"

    def test_update_current_with_empty_synonyms(self):
        """Test update_current with empty synonyms list."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "synonyms": ["CO2"],
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(synonyms=[])
        assert (
            nf.current.synonyms == []
        ), f"Expected current.synonyms to be empty list, but got {nf.current.synonyms!r}"

    def test_update_current_with_none_location(self):
        """Test update_current with None location."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "location": "US",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        nf.update_current(location=None)
        assert (
            nf.current.location is None
        ), f"Expected current.location to be None, but got {nf.current.location!r}"

    def test_update_current_with_oxidation_state(self):
        """Test update_current with oxidation_state parameter."""
        data = {
            "name": "Iron(II) oxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Note: oxidation_state is extracted from name during normalization
        # This test verifies we can update it if needed
        from flowmapper.fields import OxidationState

        nf.update_current(oxidation_state=3)
        assert (
            nf.current.oxidation_state.value == 3
        ), f"Expected current.oxidation_state to be 3, but got {nf.current.oxidation_state.value if nf.current.oxidation_state else None!r}"


class TestNormalizedFlowRepr:
    """Test NormalizedFlow __repr__ method."""

    def test_repr_basic_normalized_flow(self):
        """Test NormalizedFlow __repr__ with basic flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        result = repr(nf)
        assert "NormalizedFlow(" in result, "Expected 'NormalizedFlow(' in repr"
        assert "original=" in result, "Expected 'original=' in repr"
        assert "current=" in result, "Expected 'current=' in repr"
        assert "matched=" in result, "Expected 'matched=' in repr"

    def test_repr_shows_original_and_current(self):
        """Test NormalizedFlow __repr__ shows both original and current flows."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        result = repr(nf)
        # Check that original Flow repr is included
        assert "Flow(" in result, "Expected 'Flow(' in repr (from original or current)"
        # Check that both original and current are represented
        assert result.count("Flow(") >= 2, "Expected at least 2 Flow() representations"

    def test_repr_with_matched_true(self):
        """Test NormalizedFlow __repr__ with matched=True."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original,
            normalized=normalized,
            current=copy(normalized),
            matched=True,
        )

        result = repr(nf)
        assert "matched=True" in result, "Expected 'matched=True' in repr"

    def test_repr_with_matched_false(self):
        """Test NormalizedFlow __repr__ with matched=False."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original,
            normalized=normalized,
            current=copy(normalized),
            matched=False,
        )

        result = repr(nf)
        assert "matched=False" in result, "Expected 'matched=False' in repr"

    def test_repr_with_modified_current(self):
        """Test NormalizedFlow __repr__ shows modified current flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify current
        nf.update_current(name="Modified name")

        result = repr(nf)
        assert (
            "Modified name" in result or "modified name" in result
        ), "Expected modified name in repr"
        # Original should still be in repr
        assert (
            "Carbon dioxide" in result or "carbon dioxide" in result
        ), "Expected original name in repr"

    def test_repr_with_all_fields(self):
        """Test NormalizedFlow __repr__ with flows containing all fields."""
        data = {
            "name": "Carbon dioxide, in air",
            "context": ["Raw", "(unspecified)"],
            "unit": "kg",
            "identifier": "test-id-123",
            "location": "US",
            "cas_number": "000124-38-9",
            "synonyms": ["CO2"],
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        result = repr(nf)
        # Should include information from both original and current
        assert "original=" in result, "Expected 'original=' in repr"
        assert "current=" in result, "Expected 'current=' in repr"
        # The Flow reprs should include their fields
        assert (
            "identifier=" in result or "test-id-123" in result
        ), "Expected identifier in repr"

    def test_repr_multiline_format(self):
        """Test NormalizedFlow __repr__ uses multiline format."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        result = repr(nf)
        # Should be multiline (contains newlines)
        assert "\n" in result, "Expected multiline repr format"
        assert result.count("\n") >= 2, "Expected at least 2 newlines in repr"

    def test_repr_original_and_current_different(self):
        """Test NormalizedFlow __repr__ when original and current differ."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        original = Flow.from_dict(data)
        normalized = original.normalize()
        nf = NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

        # Modify current significantly
        nf.update_current(name="Water", unit="g", location="US")

        result = repr(nf)
        # Both should be represented
        assert "original=" in result, "Expected 'original=' in repr"
        assert "current=" in result, "Expected 'current=' in repr"
        # Original name should be present
        assert (
            "Carbon dioxide" in result or "carbon dioxide" in result
        ), "Expected original name in repr"
        # Modified name should be present
        assert "Water" in result or "water" in result, "Expected modified name in repr"


class TestNormalizedFlowFromDict:
    """Test NormalizedFlow from_dict static method."""

    def test_from_dict_creates_normalized_flow(self):
        """Test from_dict creates NormalizedFlow from dictionary."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        nf = NormalizedFlow.from_dict(data)

        assert isinstance(nf, NormalizedFlow), "Expected NormalizedFlow instance"
        assert nf.original.name.data == "Carbon dioxide", "Expected original name"
        assert nf.normalized.name.data == "carbon dioxide", "Expected normalized name"
        assert nf.current.name.data == "carbon dioxide", "Expected current name"

    def test_from_dict_sets_original_correctly(self):
        """Test from_dict sets original flow correctly."""
        data = {
            "name": "Carbon dioxide, NL",
            "context": "air",
            "unit": "kg",
            "location": "US",
        }
        nf = NormalizedFlow.from_dict(data)

        assert (
            nf.original.name.data == "Carbon dioxide, NL"
        ), "Expected original name preserved"
        assert nf.original.location == "US", "Expected original location preserved"

    def test_from_dict_sets_normalized_correctly(self):
        """Test from_dict sets normalized flow correctly."""
        data = {
            "name": "Carbon dioxide, NL",
            "context": "air",
            "unit": "kg",
        }
        nf = NormalizedFlow.from_dict(data)

        # Normalized should extract location from name
        assert (
            nf.normalized.location == "NL"
        ), "Expected normalized location extracted from name"
        assert (
            nf.normalized.name.data == "carbon dioxide"
        ), "Expected normalized name without location"

    def test_from_dict_sets_current_as_copy_of_normalized(self):
        """Test from_dict sets current as copy of normalized."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        nf = NormalizedFlow.from_dict(data)

        assert (
            nf.current.name.data == nf.normalized.name.data
        ), "Expected current equals normalized"
        assert (
            nf.current is not nf.normalized
        ), "Expected current is a copy, not same object"


class TestNormalizedFlowUnitCompatible:
    """Test NormalizedFlow unit_compatible method."""

    def test_unit_compatible_same_units(self):
        """Test unit_compatible with same units."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Methane", "context": "air", "unit": "kg"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        assert nf1.unit_compatible(nf2) is True, "Expected same units to be compatible"

    def test_unit_compatible_different_compatible_units(self):
        """Test unit_compatible with different but compatible units."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Methane", "context": "air", "unit": "g"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        assert nf1.unit_compatible(nf2) is True, "Expected kg and g to be compatible"

    def test_unit_compatible_incompatible_units(self):
        """Test unit_compatible with incompatible units."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Water", "context": "water", "unit": "m3"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        assert (
            nf1.unit_compatible(nf2) is False
        ), "Expected kg and m3 to be incompatible"


class TestNormalizedFlowConversionFactor:
    """Test NormalizedFlow conversion_factor method."""

    def test_conversion_factor_same_units(self):
        """Test conversion_factor for same units (should be 1.0)."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Methane", "context": "air", "unit": "kg"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        assert result == 1.0, f"Expected conversion_factor to be 1.0, but got {result}"

    def test_conversion_factor_compatible_units(self):
        """Test conversion_factor for compatible units."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Methane", "context": "air", "unit": "g"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        assert (
            result == 1000.0
        ), f"Expected conversion_factor to be 1000.0 (kg to g), but got {result}"

    def test_conversion_factor_reverse_direction(self):
        """Test conversion_factor in reverse direction."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "g"}
        data2 = {"name": "Methane", "context": "air", "unit": "kg"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        assert (
            result == 0.001
        ), f"Expected conversion_factor to be 0.001 (g to kg), but got {result}"

    def test_conversion_factor_incompatible_units(self):
        """Test conversion_factor with incompatible units returns NaN."""
        import math

        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Water", "context": "water", "unit": "m3"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        assert math.isnan(
            result
        ), f"Expected conversion_factor to be NaN for incompatible units, but got {result}"

    def test_conversion_factor_with_transformation_factor(self):
        """Test conversion_factor multiplies transformation factor by unit conversion."""
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "conversion_factor": 2.5,
        }
        data2 = {"name": "Methane", "context": "air", "unit": "g"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        # transformation_factor (2.5) * unit_conversion (1000.0 kg to g) = 2500.0
        assert (
            result == 2500.0
        ), f"Expected conversion_factor to be 2500.0 (2.5 * 1000.0), but got {result}"

    def test_conversion_factor_with_transformation_factor_reverse(self):
        """Test conversion_factor with transformation factor in reverse direction."""
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "g",
            "conversion_factor": 0.5,
        }
        data2 = {"name": "Methane", "context": "air", "unit": "kg"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        # transformation_factor (0.5) * unit_conversion (0.001 g to kg) = 0.0005
        assert (
            result == 0.0005
        ), f"Expected conversion_factor to be 0.0005 (0.5 * 0.001), but got {result}"

    def test_conversion_factor_with_transformation_factor_same_units(self):
        """Test conversion_factor with transformation factor but same units."""
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "conversion_factor": 3.0,
        }
        data2 = {"name": "Methane", "context": "air", "unit": "kg"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        # transformation_factor (3.0) * unit_conversion (1.0 same units) = 3.0
        assert (
            result == 3.0
        ), f"Expected conversion_factor to be 3.0 (3.0 * 1.0), but got {result}"

    def test_conversion_factor_with_none_transformation_factor(self):
        """Test conversion_factor when transformation_factor is None (defaults to 1.0)."""
        data1 = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        data2 = {"name": "Methane", "context": "air", "unit": "g"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        # Ensure conversion_factor is None
        assert (
            nf1.current.conversion_factor is None
        ), "Expected conversion_factor to be None"

        result = nf1.conversion_factor(nf2)
        # None defaults to 1.0, so 1.0 * 1000.0 = 1000.0
        assert (
            result == 1000.0
        ), f"Expected conversion_factor to be 1000.0 (1.0 * 1000.0), but got {result}"

    def test_conversion_factor_with_transformation_factor_zero(self):
        """Test conversion_factor with transformation_factor of 0.0.

        Note: Due to Python's 'or' operator behavior, 0.0 is treated as falsy
        and defaults to 1.0, so the result is 1.0 * unit_conversion.
        """
        data1 = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "conversion_factor": 0.0,
        }
        data2 = {"name": "Methane", "context": "air", "unit": "g"}

        nf1 = NormalizedFlow.from_dict(data1)
        nf2 = NormalizedFlow.from_dict(data2)

        result = nf1.conversion_factor(nf2)
        # Due to 'or 1.0', 0.0 is treated as falsy and defaults to 1.0
        # So: 1.0 * unit_conversion (1000.0) = 1000.0
        assert (
            result == 1000.0
        ), f"Expected conversion_factor to be 1000.0 (1.0 * 1000.0 due to 'or' behavior), but got {result}"


class TestNormalizedFlowExport:
    """Test NormalizedFlow export method."""

    def test_export_exports_original_flow_data(self):
        """Test export exports original flow data."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        nf = NormalizedFlow.from_dict(data)
        result = nf.export()

        assert result["name"] == "Carbon dioxide", "Expected original name in export"
        assert result["unit"] == "kg", "Expected original unit in export"
        # Context.value returns the original value (string in this case)
        assert result["context"] == "air", "Expected original context in export"

    def test_export_only_non_none_values(self):
        """Test export only includes non-None values."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
        }
        nf = NormalizedFlow.from_dict(data)
        result = nf.export()

        assert "identifier" not in result, "Expected identifier not in export when None"
        assert "location" not in result, "Expected location not in export when None"

    def test_export_includes_location_when_present(self):
        """Test export includes location when present."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "location": "NL",
        }
        nf = NormalizedFlow.from_dict(data)
        result = nf.export()

        assert "location" in result, "Expected location in export when present"
        assert result["location"] == "NL", "Expected location value in export"

    def test_export_includes_identifier_when_present(self):
        """Test export includes identifier when present."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "identifier": "test-id-123",
        }
        nf = NormalizedFlow.from_dict(data)
        result = nf.export()

        assert "identifier" in result, "Expected identifier in export when present"
        assert (
            result["identifier"] == "test-id-123"
        ), "Expected identifier value in export"

    def test_export_cas_number_correctly(self):
        """Test CAS number is exported correctly."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "cas_number": "000124-38-9",
        }
        nf = NormalizedFlow.from_dict(data)
        result = nf.export()

        assert "cas_number" in result, "Expected cas_number in export when present"
        # CAS number is exported from normalized flow
        assert isinstance(result["cas_number"], str), "Expected cas_number to be string"


class TestNormalizedFlowProperties:
    """Test NormalizedFlow property accessors."""

    def test_properties_return_current_flow_values(self):
        """Test properties return correct value from current flow."""
        data = {
            "name": "Carbon dioxide",
            "context": "air",
            "unit": "kg",
            "location": "NL",
            "identifier": "test-id",
        }
        nf = NormalizedFlow.from_dict(data)

        assert nf.name == "carbon dioxide", "Expected name property from current"
        # Unit is normalized, so "kg" becomes "kilogram"
        assert nf.unit == "kilogram", "Expected unit property from current (normalized)"
        assert nf.context == ("air",), "Expected context property from current"
        assert nf.location == "NL", "Expected location property from current"
        assert nf.identifier == "test-id", "Expected identifier property from current"

    def test_properties_reflect_update_current(self):
        """Test properties reflect changes after update_current()."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        nf = NormalizedFlow.from_dict(data)

        original_name = nf.name
        nf.update_current(name="Modified name", unit="g")

        # Name is not normalized when passed to update_current via Flow.from_dict
        assert nf.name == "Modified name", "Expected name property to reflect update"
        # Unit is not normalized when passed to update_current via Flow.from_dict
        assert nf.unit == "g", "Expected unit property to reflect update"
        assert nf.name != original_name, "Expected name to change after update"

    def test_properties_reflect_reset_current(self):
        """Test properties reflect reset after reset_current()."""
        data = {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        nf = NormalizedFlow.from_dict(data)

        normalized_name = nf.name
        nf.update_current(name="Modified name")
        assert nf.name != normalized_name, "Expected name to change after update"

        nf.reset_current()
        assert nf.name == normalized_name, "Expected name to reset after reset_current"
