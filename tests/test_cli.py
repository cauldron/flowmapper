import json

from typer.testing import CliRunner

from flowmapper.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.output.startswith(
        "flowmapper, version"
    ), f"Expected result.output to start with 'flowmapper, version', but got {result.output[:50]!r}"


def test_format_glad(tmp_path):
    result = runner.invoke(
        app,
        [
            "map",
            "tests/data/sp.json",
            "tests/data/ei-3.7.json",
            "--format",
            "glad",
            "--output-dir",
            str(tmp_path),
        ],
    )
    expected_files = sorted(
        [
            tmp_path / "sp-ei-3.7.xlsx",
            tmp_path / "sp-ei-3.7-unmatched-source.json",
            tmp_path / "sp-ei-3.7-unmatched-target.json",
        ]
    )

    files = sorted(tmp_path.glob("**/*"))

    assert (
        result.exit_code == 0
    ), f"Expected exit_code to be 0, but got {result.exit_code}"
    assert (
        expected_files == files
    ), f"Expected files to be {expected_files}, but got {files}"


def test_format_randonneur(tmp_path):
    result = runner.invoke(
        app,
        [
            "map",
            "tests/data/sp.json",
            "tests/data/ei-3.7.json",
            "--format",
            "randonneur",
            "--output-dir",
            str(tmp_path),
        ],
    )
    expected_files = sorted(
        [
            tmp_path / "sp-ei-3.7.json",
            tmp_path / "sp-ei-3.7-unmatched-source.json",
            tmp_path / "sp-ei-3.7-unmatched-target.json",
        ]
    )

    files = sorted(tmp_path.glob("**/*"))

    assert (
        result.exit_code == 0
    ), f"Expected exit_code to be 0, but got {result.exit_code}"
    assert (
        expected_files == files
    ), f"Expected files to be {expected_files}, but got {files}"


def test_matched_flows(tmp_path):
    runner.invoke(
        app,
        [
            "map",
            "tests/data/sp.json",
            "tests/data/ei-3.7.json",
            "--matched-source",
            "--matched-target",
            "--output-dir",
            str(tmp_path),
        ],
    )

    with open(tmp_path / "sp-ei-3.7-matched-source.json") as fs:
        actual = json.load(fs)

    expected = [
        {
            "cas_number": "110-63-4",
            "context": "air",
            "name": "1,4-Butanediol",
            "unit": "kg",
        },
        {"context": "air/low. pop.", "name": "Ammonia, FR", "unit": "kg"},
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_matched_flows_with_randonneur_transformations(tmp_path):
    runner.invoke(
        app,
        [
            "map",
            "tests/data/sp.json",
            "tests/data/ei-3.7.json",
            "--transformations",
            "tests/data/transformations.json",
            "--matched-source",
            "--matched-target",
            "--output-dir",
            str(tmp_path),
        ],
    )

    with open(tmp_path / "sp-ei-3.7-matched-source.json") as fs:
        actual = json.load(fs)

    expected = [
        {
            "cas_number": "110-63-4",
            "context": "air",
            "name": "1,4-Butanediol",
            "unit": "kg",
        },
        {
            "cas_number": "110-63-4",
            "context": "air/high. pop.",
            "name": "1,4-Butanediol",
            "unit": "kg",
        },
        {"context": "air/low. pop.", "name": "Ammonia, FR", "unit": "kg"},
        {"context": "air/low. pop.", "name": "Ammonia, as N", "unit": "kg"},
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"


def test_matched_flows_with_multiple_randonneur_transformations(tmp_path):
    runner.invoke(
        app,
        [
            "map",
            "tests/data/sp.json",
            "tests/data/ei-3.7.json",
            "--transformations",
            "tests/data/transformations.json",
            "--transformations",
            "tests/data/migrations.json",
            "--matched-source",
            "--matched-target",
            "--output-dir",
            str(tmp_path),
        ],
    )

    with open(tmp_path / "sp-ei-3.7-matched-source.json") as fs:
        actual = json.load(fs)

    expected = [
        {
            "name": "1,4-Butanediol",
            "unit": "kg",
            "context": "air",
            "cas_number": "110-63-4",
        },
        {
            "name": "1,4-Butanediol",
            "unit": "kg",
            "context": "air/high. pop.",
            "cas_number": "110-63-4",
        },
        {"name": "Ammonia, FR", "unit": "kg", "context": "air/low. pop."},
        {"name": "Ammonia, as N", "unit": "kg", "context": "air/low. pop."},
    ]
    assert (
        actual == expected
    ), f"Expected actual to equal expected, but got {actual} instead of {expected}"
