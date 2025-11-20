"""File I/O utility functions."""

import importlib.resources as resource
import json
from pathlib import Path

from flowmapper.utils.constants import RESULTS_DIR


def load_standard_transformations() -> list:
    """Load standard transformation files."""
    # with resource.as_file(
    #     resource.files("flowmapper") / "data" / "standard-units-harmonization.json"
    # ) as filepath:
    #     units = json.load(open(filepath))
    with resource.as_file(
        resource.files("flowmapper") / "data" / "simapro-2023-ecoinvent-3-contexts.json"
    ) as filepath:
        contexts = json.load(open(filepath))
    # return [units, contexts]
    return [contexts]


def read_migration_files(*filepaths: str | Path) -> list[dict]:
    """
    Read and aggregate migration data from multiple JSON files.

    This function opens and reads a series of JSON files, each containing migration data as a list of dicts without the change type.
    It aggregates all changes into a single list and returns it wrapped in a dictionary
    under the change type 'update'.

    Parameters
    ----------
    *filepaths : Path
        Variable length argument list of Path objects.

    Returns
    -------
    dict
        A dictionary containing a single key 'update', which maps to a list. This list is
        an aggregation of the data from all the JSON files read.
    """
    migration_data = []

    for filepath in filepaths:
        if (RESULTS_DIR / filepath).is_file():
            filepath = RESULTS_DIR / filepath
        with open(Path(filepath)) as fs:
            migration_data.append(json.load(fs))

    return migration_data
