import importlib.metadata
import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from flowmapper.extraction import ecospold2_biosphere_extractor, simapro_csv_biosphere_extractor
from flowmapper.main import OutputFormat, flowmapper

logger = logging.getLogger(__name__)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"flowmapper, version {importlib.metadata.version('flowmapper')}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """
    Generate mappings between elementary flows lists
    """


@app.command()
def map(
    source: Annotated[Path, typer.Argument(help="Path to source flowlist")],
    target: Annotated[Path, typer.Argument(help="Path to target flowlist")],
    output_dir: Annotated[
        Path, typer.Option(help="Directory to save mapping and diagnostics files")
    ] = Path("."),
    format: Annotated[
        OutputFormat,
        typer.Option(help="Mapping file output format", case_sensitive=False),
    ] = "all",
    default_transformations: Annotated[
        bool, typer.Option(help="Include default context and unit transformations?")
    ] = True,
    transformations: Annotated[
        Optional[list[Path]],
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
):
    return flowmapper(
        source=source,
        target=target,
        output_dir=output_dir,
        format=format,
        default_transformations=default_transformations,
        transformations=transformations,
        unmatched_source=unmatched_source,
        unmatched_target=unmatched_target,
        matched_source=matched_source,
        matched_target=matched_target,
    )


@app.command()
def extract_simapro_csv(
    simapro_csv_filepath: Annotated[
        Path, typer.Argument(help="Path to source SimaPro CSV file")
    ],
    output_dir: Annotated[
        Path, typer.Argument(help="Directory to save mapping and diagnostics files")
    ],
) -> None:
    simapro_csv_biosphere_extractor(simapro_csv_filepath, output_dir)


@app.command()
def extract_ecospold2(
    elementary_exchanges_filepath: Annotated[
        Path, typer.Argument(help="Path to source `ElementaryExchanges.xml` file")
    ],
    output_dir: Annotated[
        Path, typer.Argument(help="Directory to save mapping and diagnostics files")
    ],
) -> None:
    ecospold2_biosphere_extractor(elementary_exchanges_filepath, output_dir)
