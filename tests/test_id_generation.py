from flowmapper.utils import generate_flow_id


def test_generate_flow_id():
    flow1 = {
        "name": "1,4-Butanediol",
        "context": ["Air", "(unspecified)"],
        "unit": "kg",
        "CAS number": "000110-63-4",
    }
    actual = generate_flow_id(flow1)
    expected = "77bb0c932afd7d7eb7ada382c8828b9f"
    assert actual == expected, f"Expected generate_flow_id(flow1) to equal '{expected}', but got {actual!r}"
