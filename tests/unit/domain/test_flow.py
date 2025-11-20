import pytest

from flowmapper.domain import Flow


class TestFlowRepr:
    """Test Flow __repr__ method."""

    def test_repr_basic_flow(self):
        """Test Flow __repr__ with only required fields."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        result = repr(flow)
        assert "Flow(" in result, "Expected 'Flow(' in repr"
        assert "name=" in result, "Expected 'name=' in repr"
        assert "unit=" in result, "Expected 'unit=' in repr"
        assert "context=" in result, "Expected 'context=' in repr"
        assert (
            "Carbon dioxide" in result or "carbon dioxide" in result
        ), "Expected name in repr"

    def test_repr_with_identifier(self):
        """Test Flow __repr__ with identifier."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": "test-id-123",
            }
        )
        result = repr(flow)
        assert "identifier=" in result, "Expected 'identifier=' in repr"
        assert "test-id-123" in result, "Expected identifier value in repr"

    def test_repr_with_location(self):
        """Test Flow __repr__ with location."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg", "location": "US"}
        )
        result = repr(flow)
        assert "location=" in result, "Expected 'location=' in repr"
        assert "US" in result, "Expected location value in repr"

    def test_repr_with_cas_number(self):
        """Test Flow __repr__ with CAS number."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "cas_number": "000124-38-9",
            }
        )
        result = repr(flow)
        assert "cas_number=" in result, "Expected 'cas_number=' in repr"
        # CAS number is normalized, so check for normalized format
        assert (
            "124-38-9" in result or "000124-38-9" in result
        ), "Expected CAS number in repr"

    def test_repr_with_synonyms(self):
        """Test Flow __repr__ with synonyms."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "synonyms": ["CO2", "carbon dioxide"],
            }
        )
        result = repr(flow)
        assert "synonyms=" in result, "Expected 'synonyms=' in repr"
        assert "CO2" in result, "Expected synonym in repr"

    def test_repr_with_all_fields(self):
        """Test Flow __repr__ with all optional fields."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": "test-id",
                "location": "US",
                "cas_number": "000124-38-9",
                "synonyms": ["CO2"],
            }
        )
        result = repr(flow)
        assert "name=" in result, "Expected 'name=' in repr"
        assert "unit=" in result, "Expected 'unit=' in repr"
        assert "context=" in result, "Expected 'context=' in repr"
        assert "identifier=" in result, "Expected 'identifier=' in repr"
        assert "location=" in result, "Expected 'location=' in repr"
        assert "cas_number=" in result, "Expected 'cas_number=' in repr"
        assert "synonyms=" in result, "Expected 'synonyms=' in repr"

    def test_repr_without_optional_fields(self):
        """Test Flow __repr__ without optional fields (should not include them)."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        result = repr(flow)
        assert (
            "identifier=" not in result
        ), "Expected 'identifier=' not in repr when None"
        assert "location=" not in result, "Expected 'location=' not in repr when None"
        assert (
            "cas_number=" not in result
        ), "Expected 'cas_number=' not in repr when None"
        assert "synonyms=" not in result, "Expected 'synonyms=' not in repr when empty"

    def test_repr_with_empty_synonyms(self):
        """Test Flow __repr__ with empty synonyms list (should not include)."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg", "synonyms": []}
        )
        result = repr(flow)
        assert (
            "synonyms=" not in result
        ), "Expected 'synonyms=' not in repr when empty list"

    def test_repr_with_oxidation_state(self):
        """Test Flow __repr__ with oxidation state."""
        flow = Flow.from_dict(
            {
                "name": "Iron(II) oxide",
                "context": "air",
                "unit": "kg",
            }
        )
        # Oxidation state is extracted during normalization, but we can set it directly

        # Create a flow with oxidation state
        normalized = flow.normalize()
        result = repr(normalized)
        # Oxidation state might be extracted from name, check if it's in repr
        # The repr will show it if it's not None
        if normalized.oxidation_state is not None:
            assert "oxidation_state=" in result, "Expected 'oxidation_state=' in repr"


class TestFlowCopyWithNewLocation:
    """Test Flow copy_with_new_location method."""

    def test_copy_with_new_location_basic(self):
        """Test copy_with_new_location with simple location replacement."""
        flow = Flow.from_dict({"name": "Ammonia, NL", "context": "air", "unit": "kg"})
        new_flow = flow.copy_with_new_location("DE")

        assert new_flow.name.data == "Ammonia, DE", "Expected name to have new location"
        assert new_flow.context == flow.context, "Expected context to be preserved"
        assert new_flow.unit == flow.unit, "Expected unit to be preserved"
        assert new_flow._id != flow._id, "Expected new Flow instance with different _id"

    def test_copy_with_new_location_preserves_attributes(self):
        """Test copy_with_new_location preserves all other attributes."""
        flow = Flow.from_dict(
            {
                "name": "Ammonia, NL",
                "context": "air",
                "unit": "kg",
                "identifier": "test-id-123",
                "location": "US",
                "cas_number": "0007664-41-7",
                "synonyms": ["NH3"],
            }
        )
        new_flow = flow.copy_with_new_location("DE")

        assert (
            new_flow.identifier == flow.identifier
        ), "Expected identifier to be preserved"
        assert (
            new_flow.cas_number == flow.cas_number
        ), "Expected cas_number to be preserved"
        assert new_flow.synonyms == flow.synonyms, "Expected synonyms to be preserved"
        assert new_flow.context == flow.context, "Expected context to be preserved"
        assert new_flow.unit == flow.unit, "Expected unit to be preserved"

    def test_copy_with_new_location_multiple_commas(self):
        """Test copy_with_new_location with multiple commas in name."""
        flow = Flow.from_dict(
            {"name": "Ammonia, pure, NL", "context": "air", "unit": "kg"}
        )
        new_flow = flow.copy_with_new_location("FR")

        assert (
            new_flow.name.data == "Ammonia, pure, FR"
        ), "Expected location at end to be replaced"

    def test_copy_with_new_location_complex_location(self):
        """Test copy_with_new_location with complex location codes."""
        flow = Flow.from_dict(
            {"name": "Ammonia, RER w/o DE+NL+NO", "context": "air", "unit": "kg"}
        )
        new_flow = flow.copy_with_new_location("GLO")

        assert (
            new_flow.name.data == "Ammonia, GLO"
        ), "Expected complex location to be replaced with simple one"

    def test_copy_with_new_location_simple_to_complex(self):
        """Test copy_with_new_location replacing simple location with complex one."""
        flow = Flow.from_dict({"name": "Ammonia, NL", "context": "air", "unit": "kg"})
        new_flow = flow.copy_with_new_location("RER w/o DE+NL+NO")

        assert (
            new_flow.name.data == "Ammonia, RER w/o DE+NL+NO"
        ), "Expected simple location to be replaced with complex one"

    def test_copy_with_new_location_raises_value_error_no_location(self):
        """Test copy_with_new_location raises ValueError when no location suffix exists."""
        flow = Flow.from_dict({"name": "Ammonia", "context": "air", "unit": "kg"})

        with pytest.raises(ValueError, match="No location suffix found"):
            flow.copy_with_new_location("DE")

    def test_copy_with_new_location_raises_value_error_dash_location(self):
        """Test copy_with_new_location raises ValueError with dash-separated location."""
        flow = Flow.from_dict({"name": "Ammonia-NL", "context": "air", "unit": "kg"})

        with pytest.raises(ValueError, match="No location suffix found"):
            flow.copy_with_new_location("DE")

    def test_copy_with_new_location_raises_value_error_location_in_middle(self):
        """Test copy_with_new_location raises ValueError when location not at end."""
        flow = Flow.from_dict(
            {"name": "Ammonia, NL, pure", "context": "air", "unit": "kg"}
        )

        with pytest.raises(ValueError, match="No location suffix found"):
            flow.copy_with_new_location("DE")

    def test_copy_with_new_location_various_locations(self):
        """Test copy_with_new_location with various location codes."""
        test_cases = [
            ("Water, DE", "FR", "Water, FR"),
            ("Water, FR", "US", "Water, US"),
            ("Water, US", "GLO", "Water, GLO"),
            ("Water, GLO", "DE", "Water, DE"),
        ]

        for name, new_location, expected_name in test_cases:
            flow = Flow.from_dict({"name": name, "context": "air", "unit": "kg"})
            new_flow = flow.copy_with_new_location(new_location)
            assert (
                new_flow.name.data == expected_name
            ), f"Expected '{expected_name}' for '{name}' -> '{new_location}', but got {new_flow.name.data!r}"

    def test_copy_with_new_location_only_location_code(self):
        """Test copy_with_new_location with only location code in name."""
        flow = Flow.from_dict({"name": ", NL", "context": "air", "unit": "kg"})
        new_flow = flow.copy_with_new_location("DE")

        assert new_flow.name.data == ", DE", "Expected location to be replaced"

    def test_copy_with_new_location_with_trailing_whitespace(self):
        """Test copy_with_new_location preserves trailing whitespace."""
        flow = Flow.from_dict({"name": "Ammonia, NL ", "context": "air", "unit": "kg"})
        new_flow = flow.copy_with_new_location("DE")

        assert (
            new_flow.name.data == "Ammonia, DE "
        ), "Expected trailing whitespace to be preserved"

    def test_copy_with_new_location_creates_new_instance(self):
        """Test copy_with_new_location creates a new Flow instance."""
        flow = Flow.from_dict({"name": "Ammonia, NL", "context": "air", "unit": "kg"})
        new_flow = flow.copy_with_new_location("DE")

        assert new_flow is not flow, "Expected new Flow instance"
        assert new_flow._id != flow._id, "Expected different _id"

    def test_copy_with_new_location_original_unchanged(self):
        """Test copy_with_new_location does not modify original flow."""
        flow = Flow.from_dict({"name": "Ammonia, NL", "context": "air", "unit": "kg"})
        original_name = flow.name.data

        new_flow = flow.copy_with_new_location("DE")

        assert (
            flow.name.data == original_name
        ), "Expected original flow name to be unchanged"
        assert (
            new_flow.name.data != original_name
        ), "Expected new flow name to be different"

    def test_copy_with_new_location_with_all_fields(self):
        """Test copy_with_new_location with flow containing all fields."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide, NL",
                "context": ("Raw", "(unspecified)"),
                "unit": "kg",
                "identifier": "test-id-123",
                "cas_number": "000124-38-9",
                "synonyms": ["CO2"],
            }
        )
        new_flow = flow.copy_with_new_location("DE")

        # Check name is updated
        assert (
            new_flow.name.data == "Carbon dioxide, DE"
        ), "Expected name to have new location"
        # Check all other fields are preserved
        assert new_flow.identifier == flow.identifier, "Expected identifier preserved"
        assert new_flow.context == flow.context, "Expected context preserved"
        assert new_flow.unit == flow.unit, "Expected unit preserved"
        assert new_flow.cas_number == flow.cas_number, "Expected cas_number preserved"
        assert new_flow.synonyms == flow.synonyms, "Expected synonyms preserved"


class TestFlowToDict:
    """Test Flow to_dict method."""

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields populated."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": "test-id-123",
                "location": "NL",
                "cas_number": "000124-38-9",
                "synonyms": ["CO2", "Carbon dioxide"],
            }
        )
        result = flow.to_dict()

        assert result["name"] == "Carbon dioxide", "Expected name in dict"
        assert result["unit"] == "kg", "Expected unit in dict"
        # Context as_tuple() returns string if value is string, tuple if list/tuple
        assert result["context"] == "air", "Expected context as string (from as_tuple)"
        assert result["identifier"] == "test-id-123", "Expected identifier in dict"
        assert result["location"] == "NL", "Expected location in dict"
        assert result["cas_number"] == flow.cas_number, "Expected cas_number in dict"
        assert result["synonyms"] == [
            "CO2",
            "Carbon dioxide",
        ], "Expected synonyms in dict"

    def test_to_dict_with_only_required_fields(self):
        """Test to_dict with only required fields."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        result = flow.to_dict()

        assert result["name"] == "Carbon dioxide", "Expected name in dict"
        assert result["unit"] == "kg", "Expected unit in dict"
        # Context as_tuple() returns string if value is string
        assert result["context"] == "air", "Expected context as string (from as_tuple)"
        assert result["identifier"] is None, "Expected identifier to be None"
        assert "location" not in result, "Expected location not in dict when None"
        assert "cas_number" not in result, "Expected cas_number not in dict when None"
        assert "synonyms" not in result, "Expected synonyms not in dict when empty"

    def test_to_dict_excludes_none_optional_fields(self):
        """Test to_dict excludes None optional fields."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": None,
            }
        )
        result = flow.to_dict()

        assert "location" not in result, "Expected location not in dict when None"
        assert (
            "oxidation_state" not in result
        ), "Expected oxidation_state not in dict when None"
        assert "cas_number" not in result, "Expected cas_number not in dict when None"
        assert "synonyms" not in result, "Expected synonyms not in dict when empty"

    def test_to_dict_excludes_empty_synonyms(self):
        """Test to_dict excludes empty synonyms list."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "synonyms": [],
            }
        )
        result = flow.to_dict()

        assert "synonyms" not in result, "Expected empty synonyms not in dict"

    def test_to_dict_context_as_tuple(self):
        """Test to_dict converts context to tuple format."""
        flow = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": ["Raw", "(unspecified)"],
                "unit": "kg",
            }
        )
        result = flow.to_dict()

        # When context is a list, as_tuple() returns a tuple (not normalized)
        assert isinstance(result["context"], tuple), "Expected context to be tuple"
        assert result["context"] == (
            "Raw",
            "(unspecified)",
        ), "Expected context tuple (not normalized in to_dict)"


class TestFlowRandonneurMapping:
    """Test Flow randonneur_mapping static method."""

    def test_randonneur_mapping_returns_dict(self):
        """Test randonneur_mapping returns dictionary structure."""
        result = Flow.randonneur_mapping()

        assert isinstance(result, dict), "Expected dict return type"
        assert "expression language" in result, "Expected expression language key"
        assert "labels" in result, "Expected labels key"

    def test_randonneur_mapping_expression_language(self):
        """Test randonneur_mapping has correct expression language."""
        result = Flow.randonneur_mapping()

        assert (
            result["expression language"] == "JSONPath"
        ), "Expected JSONPath expression language"

    def test_randonneur_mapping_all_attributes_mapped(self):
        """Test randonneur_mapping includes all Flow attributes."""
        result = Flow.randonneur_mapping()
        labels = result["labels"]

        assert "unit" in labels, "Expected unit mapping"
        assert "name" in labels, "Expected name mapping"
        assert "context" in labels, "Expected context mapping"
        assert "identifier" in labels, "Expected identifier mapping"
        assert "location" in labels, "Expected location mapping"
        assert "cas_number" in labels, "Expected cas_number mapping"
        assert "synonyms" in labels, "Expected synonyms mapping"

    def test_randonneur_mapping_jsonpath_expressions(self):
        """Test randonneur_mapping has correct JSONPath expressions."""
        result = Flow.randonneur_mapping()
        labels = result["labels"]

        assert labels["unit"] == "$.unit", "Expected unit JSONPath"
        assert labels["name"] == "$.name", "Expected name JSONPath"
        assert labels["context"] == "$.context", "Expected context JSONPath"
        assert labels["identifier"] == "$.identifier", "Expected identifier JSONPath"
        assert labels["location"] == "$.location", "Expected location JSONPath"
        assert labels["cas_number"] == "$.cas_number", "Expected cas_number JSONPath"
        assert labels["synonyms"] == "$.synonyms", "Expected synonyms JSONPath"


class TestFlowEquality:
    """Test Flow __eq__ method."""

    def test_eq_same_instance(self):
        """Test equality with same instance."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert flow == flow, "Expected flow to equal itself"

    def test_eq_different_instances_same_data(self):
        """Test different flows with same data are not equal (different _id)."""
        flow1 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        flow2 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert flow1 != flow2, "Expected flows with different _id to not be equal"

    def test_eq_different_objects(self):
        """Test equality with non-Flow objects returns False."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert flow != "not a flow", "Expected flow to not equal string"
        assert flow != 123, "Expected flow to not equal number"
        assert flow != None, "Expected flow to not equal None"  # noqa: E711


class TestFlowComparison:
    """Test Flow __lt__ method."""

    def test_lt_sorts_by_name(self):
        """Test sorting by name."""
        flow1 = Flow.from_dict({"name": "Ammonia", "context": "air", "unit": "kg"})
        flow2 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert flow1 < flow2, "Expected Ammonia < Carbon dioxide"
        assert not (flow2 < flow1), "Expected Carbon dioxide not < Ammonia"

    def test_lt_sorts_by_unit_when_names_equal(self):
        """Test sorting by unit when names are equal."""
        flow1 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "g"}
        )
        flow2 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        assert flow1 < flow2, "Expected g < kg when names are equal"

    def test_lt_sorts_by_context_when_name_and_unit_equal(self):
        """Test sorting by context when name and unit are equal."""
        flow1 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )
        flow2 = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "water", "unit": "kg"}
        )

        assert flow1 < flow2, "Expected air < water when name and unit are equal"

    def test_lt_sorts_by_identifier_when_other_fields_equal(self):
        """Test sorting by identifier when other fields are equal."""
        flow1 = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": "id1",
            }
        )
        flow2 = Flow.from_dict(
            {
                "name": "Carbon dioxide",
                "context": "air",
                "unit": "kg",
                "identifier": "id2",
            }
        )

        assert flow1 < flow2, "Expected id1 < id2 when other fields are equal"

    def test_lt_with_non_flow_object(self):
        """Test comparison with non-Flow objects."""
        flow = Flow.from_dict(
            {"name": "Carbon dioxide", "context": "air", "unit": "kg"}
        )

        # __lt__ should return False for non-Flow objects
        result = flow < "not a flow"
        assert result is False, "Expected __lt__ to return False for non-Flow objects"
