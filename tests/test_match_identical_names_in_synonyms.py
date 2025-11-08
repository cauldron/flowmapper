from flowmapper.flow import Flow
from flowmapper.match import match_identical_names_in_synonyms


def test_match_identical_names_in_synonyms(transformations):
    source = {
        "name": "Sulfuric acid",
        "unit": "kg",
        "context": ["Emissions to water", ""],
    }

    target = {
        "identifier": "8570c45a-8c78-4709-9b8f-fb88314d9e9d",
        "chemical formula": "H8N2O4S",
        "cas_number": "007783-20-2",
        "name": "Ammonium sulfate",
        "unit": "kg",
        "context": ["water", "unspecified"],
        "synonyms": [
            "Diammonium sulfate",
            "Mascagnite",
            "Sulfuric acid",
            "Actamaster",
            "Diammonium salt",
            "Dolamin",
        ],
    }

    s = Flow(source, transformations)
    t = Flow(target, transformations)

    result = match_identical_names_in_synonyms(s, t, [], [])
    assert result, f"Expected match_identical_names_in_synonyms to return a truthy value, but got {result}"
