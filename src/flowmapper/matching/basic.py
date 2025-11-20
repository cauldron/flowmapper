"""Basic matching functions.

This module contains basic matching functions that match flows based on
identical or similar attributes without transformations.
"""

from rapidfuzz.distance.DamerauLevenshtein import distance

from flowmapper.domain import MatchCondition, NormalizedFlow
from flowmapper.matching.core import get_matches
from flowmapper.utils import toolz


def match_identical_identifier(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
) -> list:
    """Match flows with identical identifiers.

    This function groups source flows by their identifier and matches them
    to target flows with the same identifier. Only flows with non-None
    identifiers are considered.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.exact for flows with
        matching identifiers.

    Notes
    -----
    - Only flows with non-None identifiers are matched
    - If multiple target flows share the same identifier, `get_matches` will
      only allow a single result target per source flow
    - Match condition is always MatchCondition.exact
    """
    matches = []

    for source_id, sources in toolz.itertoolz.groupby(
        lambda x: x.identifier, source_flows
    ).items():
        if not source_id:
            continue
        matches.extend(
            get_matches(
                source_flows=sources,
                # Filter target flows with matching identifier. We don't need to worry about
                # duplicate identifiers as `get_matches` will only allow a single result target
                target_flows=[
                    flow for flow in target_flows if source_id == flow.identifier
                ],
                comment=f"Shared target-unique identifier: {source_id}",
                function_name="match_identical_identifier",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_identical_cas_numbers(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows with identical CAS numbers, context, and location.

    This function matches flows that share the same CAS (Chemical Abstracts
    Service) registry number, context, and location. All three attributes
    must match exactly.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.exact for flows with
        matching CAS numbers, context, and location.

    Notes
    -----
    - CAS number, context, and location must all match exactly
    - Match condition is always MatchCondition.exact
    - Only unit-compatible flows are matched
    """
    matches = []

    for (cas_number, context, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.cas_number, x.context, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.cas_number == cas_number
                    and flow.context == context
                    and flow.location == location
                ],
                comment=f"Shared CAS code with identical context and location: {cas_number}",
                function_name="match_identical_cas_numbers",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_identical_names(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows with identical normalized names, context, oxidation state, and location.

    This is one of the most precise matching functions, requiring exact matches
    on normalized name, context, oxidation state, and location. All four
    attributes must match exactly.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.exact for flows with
        identical normalized names, context, oxidation state, and location.

    Notes
    -----
    - All four attributes (name, context, oxidation_state, location) must match exactly
    - Names are compared after normalization
    - Match condition is always MatchCondition.exact
    - Only unit-compatible flows are matched
    """
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    target
                    for target in target_flows
                    if target.name == name
                    and target.context == context
                    and target.oxidation_state == oxidation_state
                    and target.location == location
                ],
                comment=f"Shared normalized name with identical context, oxidation state, and location: {name}",
                function_name="match_identical_names",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_close_names(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows with similar names using Damerau-Levenshtein distance.

    This function matches flows where the normalized names have a Damerau-
    Levenshtein edit distance of less than 3, while still requiring exact
    matches on context, oxidation state, and location.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.related for flows with
        similar names (edit distance < 3) and identical context, oxidation
        state, and location.

    Notes
    -----
    - Uses Damerau-Levenshtein distance with case-insensitive comparison
    - Edit distance must be less than 3 (i.e., 0, 1, or 2)
    - Context, oxidation state, and location must still match exactly
    - Match condition is MatchCondition.related (not exact due to name differences)
    - Only unit-compatible flows are matched
    """
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    target
                    for target in target_flows
                    if distance(
                        str(target.name), str(name), processor=lambda x: x.lower()
                    )
                    < 3
                    and target.context == context
                    and target.oxidation_state == oxidation_state
                    and target.location == location
                ],
                comment=f"Name has Damerau Levenshtein edit distance of 2 or lower with identical context, oxidation state, and location: {name}",
                function_name="match_close_names",
                match_condition=MatchCondition.related,
            )
        )

    return matches


def match_identical_names_lowercase(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows with identical names when compared in lowercase.

    This function matches flows where the normalized names are identical when
    converted to lowercase, while still requiring exact matches on context,
    oxidation state, and location. This handles cases where names differ only
    in capitalization.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.close for flows with
        identical lowercase names and identical context, oxidation state,
        and location.

    Notes
    -----
    - Names are compared in lowercase (case-insensitive)
    - Context, oxidation state, and location must still match exactly
    - Match condition is MatchCondition.close (not exact due to case differences)
    - Only unit-compatible flows are matched
    """
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        name = name.lower()
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name.lower() == name
                    and flow.context == context
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized lowercase name with identical context, oxidation state, and location: {name}",
                function_name="match_identical_names_lowercase",
                match_condition=MatchCondition.close,
            )
        )

    return matches


def match_identical_names_without_commas(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows with identical names when commas are removed.

    This function matches flows where the normalized names are identical after
    removing all commas, while still requiring exact matches on context,
    oxidation state, and location. This handles cases where names differ only
    in comma placement.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.close for flows with
        identical names (after removing commas) and identical context,
        oxidation state, and location.

    Notes
    -----
    - All commas are removed from names before comparison
    - Context, oxidation state, and location must still match exactly
    - Match condition is MatchCondition.close (not exact due to comma differences)
    - Only unit-compatible flows are matched
    """
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name.replace(",", "") == name.replace(",", "")
                    and flow.context == context
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized name with commas removed and identical context, oxidation state, and location: {name}",
                match_condition=MatchCondition.close,
                function_name="match_identical_names_without_commas",
            )
        )

    return matches
