"""Shared constants and data for flowmapper utilities."""

import importlib.resources as resource
import json
from pathlib import Path

import structlog
from randonneur_data import Registry

logger = structlog.get_logger("flowmapper")
default_registry = Registry()
RESULTS_DIR = Path(__file__).parent.parent / "manual_matching" / "results"

with resource.as_file(
    resource.files("flowmapper") / "data" / "names_and_locations.json"
) as filepath:
    names_and_locations = {o["source"]: o for o in json.load(open(filepath))}

try:
    import cytoolz as toolz
except ImportError:
    logger.info("Install `cytoolz` to get a speed up in matching functions")
    import toolz

assert toolz  # Do not delete the import call stupid linter
