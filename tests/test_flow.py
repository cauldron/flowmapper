from flowmapper.cas import CASField
from flowmapper.domain import Flow
from flowmapper.transformation_mapping import prepare_transformations


def test_flow_with_transformations_repr():
    d = {
        "name": "Carbon dioxide, in air",
        "context": ["Raw", "(unspecified)"],
        "unit": "kg",
        "cas": "000124-38-9",
    }

    transformations = prepare_transformations(
        [
            {
                "update": [
                    {
                        "source": {
                            "name": "Carbon dioxide, in air",
                            "context": ["Raw", "(unspecified)"],
                        },
                        "target": {"name": "Carbon dioxide"},
                    }
                ]
            }
        ]
    )

    f = Flow(d, transformations=transformations)
    expected = """Flow object:
    Identifier: StringField with missing original value
    Name: StringField: 'Carbon dioxide, in air' -> 'carbon dioxide'
    Context: ContextField: '['Raw', '(unspecified)']' -> '('raw',)'
    Unit: UnitField: 'kg' -> 'kg'"""

    assert (
        repr(f) == expected
    ), f"Expected repr(f) to equal expected string, but got {repr(f)!r} instead of {expected!r}"


def test_flow_from_sp_categories(transformations):
    data = {
        "name": "Carbon dioxide, in air",
        "context": "resources/in air",
        "unit": "kg",
        "cas_number": "000124-38-9",
    }

    flow = Flow(data, transformations)
    assert (
        not flow.identifier
    ), f"Expected flow.identifier to be falsy, but got {flow.identifier}"
    assert (
        flow.name.original == "Carbon dioxide, in air"
    ), f"Expected flow.name.original to be 'Carbon dioxide, in air', but got {flow.name.original!r}"
    assert (
        flow.name.normalized == "carbon dioxide, in air"
    ), f"Expected flow.name.normalized to be 'carbon dioxide, in air', but got {flow.name.normalized!r}"
    assert (
        flow.context.original == "resources/in air"
    ), f"Expected flow.context.original to be 'resources/in air', but got {flow.context.original!r}"
    assert flow.context.normalized == (
        "natural resource",
        "in air",
    ), f"Expected flow.context.normalized to be ('natural resource', 'in air'), but got {flow.context.normalized!r}"


def test_flow_from_sp_missing(transformations):
    data = {"name": "Chrysotile", "context": "Raw/in ground", "unit": "kg"}

    flow = Flow(data, transformations)
    assert (
        flow.name.original == "Chrysotile"
    ), f"Expected flow.name.original to be 'Chrysotile', but got {flow.name.original!r}"
    expected = """Flow object:
    Identifier: StringField with missing original value
    Name: StringField: 'Chrysotile' -> 'chrysotile'
    Context: ContextField: 'Raw/in ground' -> '('natural resource', 'in ground')'
    Unit: UnitField: 'kg' -> 'kg'"""
    assert (
        repr(flow) == expected
    ), f"Expected repr(flow) to equal expected string, but got {repr(flow)!r} instead of {expected!r}"
    assert (
        flow.context.original == "Raw/in ground"
    ), f"Expected flow.context.original to be 'Raw/in ground', but got {flow.context.original!r}"
    assert flow.context.normalized == (
        "natural resource",
        "in ground",
    ), f"Expected flow.context.normalized to be ('natural resource', 'in ground'), but got {flow.context.normalized!r}"


def test_flow_cas():
    data = {
        "name": "Actinium",
        "cas_number": "007440-34-8",
        "chemical formula": "Ac\u007f",
        "synonyms": "Actinium",
        "unit": "kg",
        "Class": "Raw materials",
        "context": "Raw materials",
        "Description": "",
    }

    fields = {
        "identifier": "Flow UUID",
        "name": "name",
        "context": "context",
        "unit": "unit",
        "cas_number": "CAS No",
    }

    flow = Flow(data)
    assert flow.cas_number == CASField(
        "007440-34-8"
    ), f"Expected flow.cas to equal CASField('007440-34-8'), but got {flow.cas_number!r}"
    assert (
        flow.cas_number == "7440-34-8"
    ), f"Expected flow.cas to equal '7440-34-8', but got {flow.cas_number!r}"


def test_flow_from_ei():
    data = {
        "name": "1,3-Dioxolan-2-one",
        "cas_number": "000096-49-1",
        "chemical formula": "",
        "synonyms": "",
        "unit": "kg",
        "Class": "chemical",
        "ExternalReference": "",
        "Preferred": "",
        "context": "water/unspecified",
        "identifier": "5b7d620e-2238-5ec9-888a-6999218b6974",
        "AltUnit": "",
        "Var": "",
        "Second CAS": "96-49-1",
    }
    flow = Flow(data)
    assert (
        flow.identifier == "5b7d620e-2238-5ec9-888a-6999218b6974"
    ), f"Expected flow.identifier to be '5b7d620e-2238-5ec9-888a-6999218b6974', but got {flow.identifier!r}"


def test_flow_with_synonyms(transformations):
    data = {
        "identifier": "f0cc0453-32c0-48f5-b8d4-fc87d100b8d9",
        "cas_number": "000078-79-5",
        "name": "Isoprene",
        "unit": "kg",
        "context": ["air", "low population density, long-term"],
        "synonyms": [
            "2-methylbuta-1,3-diene",
            "methyl bivinyl",
            "hemiterpene",
        ],
    }

    flow = Flow(data, transformations)
    actual_synonyms = [obj.original for obj in flow.synonyms]
    expected_synonyms = [
        "2-methylbuta-1,3-diene",
        "methyl bivinyl",
        "hemiterpene",
    ]
    assert (
        actual_synonyms == expected_synonyms
    ), f"Expected flow.synonyms to be {expected_synonyms}, but got {actual_synonyms}"
