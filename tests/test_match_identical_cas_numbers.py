from deepdiff import DeepDiff

from flowmapper.flow import Flow
from flowmapper.match import match_identical_cas_numbers


def test_match_identical_cas_numbers(transformations):
    source = {
        "name": "1-Propanol",
        "CAS number": "000071-23-8",
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
        "CAS number": "000071-23-8",
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

    assert match_identical_cas_numbers(s, t, [], [])


def test_match_missing_cas_numbers(transformations):
    source = {
        "name": "1-Propanol",
        "CAS number": "",
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
        "CAS number": "",
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

    assert not match_identical_cas_numbers(s, t, [], [])
