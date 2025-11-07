from flowmapper.utils import normalize_str


def test_normalize_str():
    names = [
        "\u0075\u0308ber",
        "\u0055\u0308ber",
        "\u00fcber",
        "\u00dcber",
        "\u00dcber ",
        " \u00dcber",
        None,
    ]
    actual = {normalize_str(name) for name in names}
    expected = {"über", "Über", ""}
    assert actual == expected, f"Expected {{normalize_str(name) for name in names}} to equal {expected}, but got {actual}"
