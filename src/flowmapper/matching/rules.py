"""Matching rules configuration.

This module provides the default set of matching rules used by Flowmap.
"""

from flowmapper.matching.basic import (
    match_identical_cas_numbers,
    match_identical_identifier,
    match_identical_names,
    match_identical_names_target_uuid_identifier,
    match_identical_names_without_commas,
)
from flowmapper.matching.context import (
    match_name_and_parent_context,
    match_resources_with_wrong_subcontext,
)
from flowmapper.matching.ecoinvent import match_ecoinvent_transitive_matching
from flowmapper.matching.simapro import (
    manual_simapro_ecoinvent_mapping,
    manual_simapro_ecoinvent_mapping_add_regionalized_flows,
    manual_simapro_ecoinvent_mapping_resource_wrong_subcontext,
    simapro_ecoinvent_glad_name_matching,
)
from flowmapper.matching.specialized import (
    add_missing_regionalized_flows,
    match_names_with_suffix_removal,
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
    return [
        match_identical_identifier,
        match_identical_names,
        match_identical_names_without_commas,
        match_resources_with_wrong_subcontext,
        match_name_and_parent_context,
        match_identical_cas_numbers,
        match_names_with_suffix_removal,
    ]


def match_rules_simapro_ecoinvent():
    return [
        match_identical_identifier,
        match_identical_names,
        match_identical_names_without_commas,
        match_ecoinvent_transitive_matching,
        match_resources_with_wrong_subcontext,
        match_name_and_parent_context,
        manual_simapro_ecoinvent_mapping,
        simapro_ecoinvent_glad_name_matching,
        manual_simapro_ecoinvent_mapping_add_regionalized_flows,
        manual_simapro_ecoinvent_mapping_resource_wrong_subcontext,
        add_missing_regionalized_flows,
        match_identical_cas_numbers,
        match_identical_names_target_uuid_identifier,
        match_names_with_suffix_removal,
    ]
