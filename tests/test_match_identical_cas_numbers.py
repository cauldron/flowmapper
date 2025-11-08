
from flowmapper.flow import Flow
from flowmapper.match import match_identical_cas_numbers


def test_match_identical_cas_numbers(transformations):
    source = {
        "name": "1-Propanol",
        "cas_number": "000071-23-8",
        "checmical formula": "",
        "Synonyms": "1-Propanol",
        "unit": "kg",
        "Class": "Waterborne emissions",
        "context": "Emissions to water/groundwater",
        "Flow UUID": "8C31919B-2D42-4CAD-A10E-8084CCD6BE99",
        "Description": "Formula: C3H8O\u007f",
    }

    target = {
        "name": "Propanol",
        "cas_number": "000071-23-8",
        "checmical formula": "",
        "Synonyms": "propan-1-ol, 1-propanol, propyl alcohol, n-propanol, n-propyl alcohol",
        "unit": "kg",
        "Class": "chemical",
        "ExternalReference": "",
        "Preferred": "",
        "context": "water/ground-",
        "identifier": "85500204-9d88-40ae-9f0b-3ceba0e7a74f",
        "AltUnit": "",
        "Var": "",
        "Second CAS": "71-31-8; 19986-23-3; 71-23-8; 64118-40-7; 4712-36-1; 142583-61-7; 71-23-8",
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    # Test with t included in all_target_flows (realistic scenario)
    assert match_identical_cas_numbers(s, t, [], [t]), "Expected match_identical_cas_numbers to return True for flows with identical CAS numbers, but it returned False"


def test_match_missing_cas_numbers(transformations):
    source = {
        "name": "1-Propanol",
        "cas_number": "",
        "checmical formula": "",
        "synonyms": "1-Propanol",
        "unit": "kg",
        "Class": "Waterborne emissions",
        "context": "Emissions to water/groundwater",
        "identifier": "8C31919B-2D42-4CAD-A10E-8084CCD6BE99",
        "Description": "Formula: C3H8O\u007f",
    }

    target = {
        "name": "Propanol",
        "cas_number": "",
        "checmical formula": "",
        "synonyms": "propan-1-ol, 1-propanol, propyl alcohol, n-propanol, n-propyl alcohol",
        "unit": "kg",
        "Class": "chemical",
        "ExternalReference": "",
        "Preferred": "",
        "context": "water/ground-",
        "identifier": "85500204-9d88-40ae-9f0b-3ceba0e7a74f",
        "AltUnit": "",
        "Var": "",
        "Second CAS": "71-31-8; 19986-23-3; 71-23-8; 64118-40-7; 4712-36-1; 142583-61-7; 71-23-8",
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    assert not match_identical_cas_numbers(s, t, [], []), "Expected match_identical_cas_numbers to return False for flows with missing CAS numbers, but it returned True"


def test_match_identical_cas_numbers_multiple_matches(transformations):
    """Test that match doesn't occur when multiple flows have same CAS and context."""
    source = {
        "name": "1-Propanol",
        "cas_number": "000071-23-8",
        "checmical formula": "",
        "Synonyms": "1-Propanol",
        "unit": "kg",
        "Class": "Waterborne emissions",
        "context": "Emissions to water/groundwater",
        "Flow UUID": "8C31919B-2D42-4CAD-A10E-8084CCD6BE99",
        "Description": "Formula: C3H8O\u007f",
    }

    target1 = {
        "name": "Propanol",
        "cas_number": "000071-23-8",
        "checmical formula": "",
        "Synonyms": "propan-1-ol, 1-propanol, propyl alcohol, n-propanol, n-propyl alcohol",
        "unit": "kg",
        "Class": "chemical",
        "ExternalReference": "",
        "Preferred": "",
        "context": "water/ground-",
        "identifier": "85500204-9d88-40ae-9f0b-3ceba0e7a74f",
        "AltUnit": "",
        "Var": "",
        "Second CAS": "71-31-8; 19986-23-3; 71-23-8; 64118-40-7; 4712-36-1; 142583-61-7; 71-23-8",
    }

    target2 = {
        "name": "1-Propanol, alternative",
        "cas_number": "000071-23-8",
        "checmical formula": "",
        "Synonyms": "propanol",
        "unit": "kg",
        "Class": "chemical",
        "ExternalReference": "",
        "Preferred": "",
        "context": "water/ground-",
        "identifier": "85500204-9d88-40ae-9f0b-3ceba0e7a75g",
        "AltUnit": "",
        "Var": "",
    }

    s = Flow(source, transformations)
    t1 = Flow(target1, transformations)
    t2 = Flow(target2, transformations)

    # Both target flows have same CAS and context as source (after transformations)
    # Should not match when there are multiple flows with same CAS and context
    assert not match_identical_cas_numbers(s, t1, [], [t1, t2]), "Expected match_identical_cas_numbers to return False when multiple flows have same CAS and context, but it returned True"
