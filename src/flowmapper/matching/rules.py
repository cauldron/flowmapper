"""Matching rules configuration.

This module provides the default set of matching rules used by Flowmap.
"""

from functools import partial

from flowmapper.matching.basic import (
    match_identical_cas_numbers,
    match_identical_identifier,
    match_identical_names,
    match_identical_names_without_commas,
)
from flowmapper.matching.context import (
    match_name_and_parent_context,
    match_resources_with_wrong_subcontext,
)
from flowmapper.matching.specialized import add_missing_regionalized_flows
from flowmapper.matching.transformation import (
    match_ecoinvent_transitive_matching,
    match_with_transformation,
)


def match_rules():
    """Return the default list of matching functions.

    This function returns the default ordered list of matching functions
    used by Flowmap. The functions are applied in order, and matching
    stops once a flow is successfully matched.

    Returns
    -------
    list[Callable]
        List of matching functions to apply in order. Each function must
        accept `source_flows` and `target_flows` keyword arguments and
        return a list of Match objects.

    Notes
    -----
    - Functions are applied in order from most specific to least specific
    - Once a flow is matched, it is not considered by subsequent functions
    - Some functions are commented out and not included in the default rules
    - The list includes a specialized transformation for SimaPro 2024 to
      ecoinvent 3.10 biosphere matching

    Examples
    --------
    >>> rules = match_rules()
    >>> for rule in rules:
    ...     matches = rule(source_flows=source, target_flows=target)
    ...     # Process matches...
    """
    simple_ecoinvent = partial(
        match_with_transformation,
        transformation="ecoinvent-3.10-biosphere-simapro-2024-biosphere",
        fields=["name"],
    )
    simple_ecoinvent.__name__ = (
        "match_with_transformation_simapro_2024_to_ecoinvent_310"
    )

    return [
        match_identical_identifier,
        match_identical_names,
        # match_identical_names_lowercase,
        match_identical_names_without_commas,
        match_ecoinvent_transitive_matching,
        # match_resources_with_suffix_in_ground,
        # match_resources_with_suffix_in_water,
        # match_resources_with_suffix_in_air,
        # match_flows_with_suffix_unspecified_origin,
        match_resources_with_wrong_subcontext,
        match_name_and_parent_context,
        # match_close_names,
        simple_ecoinvent,
        # match_emissions_with_suffix_ion,
        # match_names_with_roman_numerals_in_parentheses,
        # match_names_with_location_codes,
        # match_resource_names_with_location_codes_and_parent_context,
        # match_custom_names_with_location_codes,
        match_identical_cas_numbers,
        # match_non_ionic_state,
        # match_biogenic_to_non_fossil,
        # match_identical_names_in_preferred_synonyms,
        # match_identical_names_in_synonyms,
    ]
