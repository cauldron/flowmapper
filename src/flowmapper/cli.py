import importlib.metadata
from pathlib import Path

import typer
from typing import Annotated
import structlog

from flowmapper.extraction import ecospold2_biosphere_extractor, simapro_csv_biosphere_extractor
from flowmapper.main import OutputFormat, flowmapper

try:
    from pyinstrument import Profiler
except ImportError:
    Profiler = None


logger = structlog.get_logger("flowmapper")

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"flowmapper, version {importlib.metadata.version('flowmapper')}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Generate mappings between elementary flows lists
    """


@app.command()
def map(
    source: Annotated[Path, typer.Argument(help="Path to source flow list")],
    target: Annotated[Path, typer.Argument(help="Path to target flow list")],
    output_dir: Annotated[
        Path, typer.Option(help="Directory to save mapping and diagnostics files")
    ] = Path("."),
    format: Annotated[
        OutputFormat,
        typer.Option(help="Mapping file output format", case_sensitive=False),
    ] = "randonneur",
    default_transformations: Annotated[
        bool, typer.Option(help="Include default context and unit transformations?")
    ] = True,
    transformations: Annotated[
        list[Path] | None,
        typer.Option(
            "--transformations",
            "-t",
            help="Randonneur data migration file with changes to be applied to source flows before matching. Can be included multiple times.",
        ),
    ] = None,
    unmatched_source: Annotated[
        bool,
        typer.Option(help="Write original source unmatched flows into separate file?"),
    ] = True,
    unmatched_target: Annotated[
        bool,
        typer.Option(help="Write original target unmatched flows into separate file?"),
    ] = True,
    matched_source: Annotated[
        bool,
        typer.Option(help="Write original source matched flows into separate file?"),
    ] = False,
    matched_target: Annotated[
        bool,
        typer.Option(help="Write original target matched flows into separate file?"),
    ] = False,
    profile: Annotated[
        bool,
        typer.Option(help="Profile matching code with pyinstrument"),
    ] = False,
):
    # Default generic mapping for JSON flow lists
    generic_mapping = {
        "expression language": "JSONPath",
        "labels": {
            "name": "name",
            "context": "context",
            "unit": "unit",
            "identifier": "identifier",
            "CAS number": "CAS number",
            "location": "location",
        },
    }
    
    if profile:
        if Profiler is None:
            raise ImportError("`pyinstrument` not installed")
        profiler = Profiler(interval=0.01)
        profiler.start()

    result = flowmapper(
        source=source,
        target=target,
        mapping_source=generic_mapping,
        mapping_target=generic_mapping,
        source_id=source.stem,
        target_id=target.stem,
        contributors=[{"title": "flowmapper", "roles": ["author"], "path": "https://github.com/cmutel/flowmapper"}],
        output_dir=output_dir,
        format=format,
        default_transformations=default_transformations,
        transformations=transformations,
        unmatched_source=unmatched_source,
        unmatched_target=unmatched_target,
        matched_source=matched_source,
        matched_target=matched_target,
    )

    if profile:
        profiler.stop()
        with open(f"{source.stem}-{target.stem}.html", "w") as f:
            f.write(profiler.output_html())

    return result


@app.command()
def extract_simapro_csv(
    simapro_csv_filepath: Annotated[
        Path, typer.Argument(help="Path to SimaPro CSV input file")
    ],
    output_filepath: Annotated[
        Path, typer.Argument(help="File path for JSON results data")
    ],
) -> None:
    simapro_csv_biosphere_extractor(simapro_csv_filepath, output_filepath)


@app.command()
def extract_ecospold2(
    elementary_exchanges_filepath: Annotated[
        Path, typer.Argument(help="Path to source `ElementaryExchanges.xml` file")
    ],
    output_filepath: Annotated[
        Path, typer.Argument(help="File path for JSON results data")
    ],
) -> None:
    ecospold2_biosphere_extractor(elementary_exchanges_filepath, output_filepath)
