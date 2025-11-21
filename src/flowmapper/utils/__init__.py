"""Utility functions for flowmapper.

This package contains utility functions organized by functionality:
- context: Context-related utilities
- strings: String manipulation utilities
- flow_names: Flow name processing
- randonneur: Randonneur-based transformations
- files: File I/O utilities
- constants: Shared constants and data
"""

from flowmapper.utils.constants import (
    RESULTS_DIR,
    default_registry,
    logger,
    names_and_locations,
    toolz,
)
from flowmapper.utils.context import (
    MISSING_VALUES,
    as_normalized_tuple,
    tupleize_context,
)
from flowmapper.utils.files import load_standard_transformations, read_migration_files
from flowmapper.utils.flow_names import remove_unit_slash, unit_slash
from flowmapper.utils.randonneur import (
    apply_randonneur,
    apply_transformation_and_convert_flows_to_normalized_flows,
    randonneur_as_function,
)
from flowmapper.utils.strings import normalize_str, rowercase

__all__ = [
    # Constants
    "RESULTS_DIR",
    "default_registry",
    "logger",
    "names_and_locations",
    "toolz",
    # Context
    "MISSING_VALUES",
    "as_normalized_tuple",
    "tupleize_context",
    # Strings
    "normalize_str",
    "rowercase",
    # Flow names
    "remove_unit_slash",
    "unit_slash",
    # Randonneur
    "apply_transformation_and_convert_flows_to_normalized_flows",
    "apply_randonneur",
    "randonneur_as_function",
    # Files
    "load_standard_transformations",
    "read_migration_files",
]
