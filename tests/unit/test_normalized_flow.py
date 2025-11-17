"""Unit tests for NormalizedFlow class."""

from copy import copy

import pytest

from flowmapper.domain import Flow, NormalizedFlow


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
        from flowmapper.oxidation_state import OxidationState

        nf.update_current(oxidation_state=3)
        assert (
            nf.current.oxidation_state.value == 3
        ), f"Expected current.oxidation_state to be 3, but got {nf.current.oxidation_state.value if nf.current.oxidation_state else None!r}"
