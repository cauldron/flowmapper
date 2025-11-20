"""Matching functions for flow mapping.

This package contains functions for matching flows between source and target
flow lists. Functions are organized by type:

- core: Core utilities for transformation and matching
- basic: Basic matching functions (identical names, CAS numbers, etc.)
- transformation: Transformation-based matching functions
- context: Context-based matching functions
- specialized: Specialized matching functions (regionalized flows, suffixes)
- rules: Default matching rules configuration
"""

from flowmapper.matching.basic import (
    match_close_names,
    match_identical_cas_numbers,
    match_identical_identifier,
    match_identical_names,
    match_identical_names_lowercase,
    match_identical_names_without_commas,
)
from flowmapper.matching.context import (
    match_name_and_parent_context,
    match_resources_with_wrong_subcontext,
)
from flowmapper.matching.core import get_matches, transform_and_then_match
from flowmapper.matching.rules import match_rules
from flowmapper.matching.simapro import (
    manual_simapro_ecoinvent_mapping,
    simapro_ecoinvent_glad_name_matching,
)
from flowmapper.matching.specialized import (
    add_missing_regionalized_flows,
    match_biogenic_to_non_fossil,
    match_emissions_with_suffix_ion,
    match_flows_with_suffix_unspecified_origin,
    match_identical_names_except_missing_suffix,
    match_resources_with_suffix_in_air,
    match_resources_with_suffix_in_ground,
    match_resources_with_suffix_in_water,
)
from flowmapper.matching.transformation import (
    match_ecoinvent_transitive_matching,
    match_with_transformation,
)

__all__ = [
    # Core
    "transform_and_then_match",
    "get_matches",
    # Basic
    "match_identical_identifier",
    "match_identical_cas_numbers",
    "match_identical_names",
    "match_close_names",
    "match_identical_names_lowercase",
    "match_identical_names_without_commas",
    # Transformation
    "match_ecoinvent_transitive_matching",
    "match_with_transformation",
    # Context
    "match_resources_with_wrong_subcontext",
    "match_name_and_parent_context",
    # Specialized
    "add_missing_regionalized_flows",
    "match_identical_names_except_missing_suffix",
    "match_biogenic_to_non_fossil",
    "match_resources_with_suffix_in_ground",
    "match_flows_with_suffix_unspecified_origin",
    "match_resources_with_suffix_in_water",
    "match_resources_with_suffix_in_air",
    "match_emissions_with_suffix_ion",
    # Rules
    "match_rules",
    # SimaPro
    "manual_simapro_ecoinvent_mapping",
    "simapro_ecoinvent_glad_name_matching",
]
