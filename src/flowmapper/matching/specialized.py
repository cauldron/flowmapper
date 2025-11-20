"""Specialized matching functions.

This module contains specialized matching functions for specific use cases
like regionalized flows and suffix matching.
"""

from flowmapper.domain import Flow, Match, MatchCondition, NormalizedFlow
from flowmapper.matching.core import get_matches
from flowmapper.utils import toolz


def add_missing_regionalized_flows(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    cutoff: int = 3,
) -> list[Match]:
    """Add missing regionalized flows based on existing regionalized flows.

    If a source flow has a location and there are enough target flows with
    the same name, context, and oxidation state but different locations,
    create a new target flow for the source location.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.
    cutoff : int, default=3
        Minimum number of other regions required to create a new target flow.

    Returns
    -------
    list[Match]
        List of Match objects with new_target_flow=True.
    """
    matches = []

    for (name, oxidation_state, context, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.oxidation_state, x.context, x.location),
        filter(lambda x: x.location, source_flows),
    ).items():
        other_regions = [
            flow
            for flow in target_flows
            if flow.name == name
            and flow.context == context
            and flow.oxidation_state == oxidation_state
            and flow.location
            and flow.location != location
        ]

        if len(other_regions) < cutoff:
            continue

        target = other_regions[0]

        for source in sources:
            if source.unit_compatible(target):
                matches.append(
                    Match(
                        source=source.original,
                        target=target.original.copy_with_new_location(
                            location=location
                        ),
                        function_name="add_missing_regionalized_flows",
                        comment=f"Added new target flow for location {location}, with shared name, context, and oxidation state",
                        condition=MatchCondition.related,
                        conversion_factor=source.conversion_factor(target),
                        new_target_flow=True,
                    )
                )

    return matches


def match_identical_names_except_missing_suffix(
    source_flows: list[Flow],
    target_flows: list[Flow],
    suffix: str,
    comment: str = "Identical names except missing suffix",
) -> dict:
    """Match flows where names differ only by a suffix.

    This function checks if source and target names are identical except
    for a specific suffix that may be present in one but not the other.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows (unused in current implementation).
    target_flows : list[Flow]
        List of target flows (unused in current implementation).
    suffix : str
        The suffix to check for.
    comment : str, default="Identical names except missing suffix"
        Comment to include in match.

    Returns
    -------
    dict
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function appears to be incomplete - it references `s` and `t` which
    are not defined. It may need to be refactored to work with the current
    matching function signature.
    """
    # Note: This function appears incomplete - it references undefined variables s and t
    # It may need to be refactored to match the signature of other matching functions
    if (
        (f"{s.name.normalized}, {suffix}" == t.name)
        or (f"{t.name.normalized}, {suffix}" == s.name)
        or (f"{s.name.normalized} {suffix}" == t.name)
        or (f"{t.name.normalized} {suffix}" == s.name)
    ) and s.context == t.context:
        return {"comment": comment}


def match_biogenic_to_non_fossil(
    source_flows: list[Flow],
    target_flows: list[Flow],
    comment="Biogenic to non-fossil if no better match",
):
    """Match biogenic flows to non-fossil flows.

    Note
    ----
    This function appears to be incomplete - it references `s` and `t` which
    are not defined. It may need to be refactored to work with the current
    matching function signature.
    """
    # Note: This function appears incomplete - it references undefined variables s and t
    if (
        s.name.normalized.removesuffix(", biogenic")
        == t.name.normalized.removesuffix(", non-fossil")
        and s.context == t.context
    ):
        return {"comment": comment}


def match_resources_with_suffix_in_ground(
    source_flows: list[Flow], target_flows: list[Flow]
):
    """Match resource flows that differ only by 'in ground' suffix.

    This function matches flows where names are identical except one has
    the suffix "in ground" and the other doesn't.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows to match.
    target_flows : list[Flow]
        List of target flows to match against.

    Returns
    -------
    dict | None
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function uses `match_identical_names_except_missing_suffix` which
    may be incomplete in its current implementation.
    """
    return match_identical_names_except_missing_suffix(
        source_flows,
        target_flows,
        suffix="in ground",
        comment="Resources with suffix in ground",
    )


def match_flows_with_suffix_unspecified_origin(
    source_flows: list[Flow], target_flows: list[Flow]
):
    """Match flows that differ only by 'unspecified origin' suffix.

    This function matches flows where names are identical except one has
    the suffix "unspecified origin" and the other doesn't.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows to match.
    target_flows : list[Flow]
        List of target flows to match against.

    Returns
    -------
    dict | None
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function uses `match_identical_names_except_missing_suffix` which
    may be incomplete in its current implementation.
    """
    return match_identical_names_except_missing_suffix(
        source_flows,
        target_flows,
        suffix="unspecified origin",
        comment="Flows with suffix unspecified origin",
    )


def match_resources_with_suffix_in_water(
    source_flows: list[Flow], target_flows: list[Flow]
):
    """Match resource flows that differ only by 'in water' suffix.

    This function matches flows where names are identical except one has
    the suffix "in water" and the other doesn't.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows to match.
    target_flows : list[Flow]
        List of target flows to match against.

    Returns
    -------
    dict | None
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function uses `match_identical_names_except_missing_suffix` which
    may be incomplete in its current implementation.
    """
    return match_identical_names_except_missing_suffix(
        source_flows,
        target_flows,
        suffix="in water",
        comment="Resources with suffix in water",
    )


def match_resources_with_suffix_in_air(
    source_flows: list[Flow], target_flows: list[Flow]
):
    """Match resource flows that differ only by 'in air' suffix.

    This function matches flows where names are identical except one has
    the suffix "in air" and the other doesn't.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows to match.
    target_flows : list[Flow]
        List of target flows to match against.

    Returns
    -------
    dict | None
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function uses `match_identical_names_except_missing_suffix` which
    may be incomplete in its current implementation.
    """
    return match_identical_names_except_missing_suffix(
        source_flows,
        target_flows,
        suffix="in air",
        comment="Resources with suffix in air",
    )


def match_emissions_with_suffix_ion(source_flows: list[Flow], target_flows: list[Flow]):
    """Match emission flows that differ only by 'ion' suffix.

    This function matches flows where names are identical except one has
    the suffix "ion" and the other doesn't.

    Parameters
    ----------
    source_flows : list[Flow]
        List of source flows to match.
    target_flows : list[Flow]
        List of target flows to match against.

    Returns
    -------
    dict | None
        Dictionary with match information if match found, None otherwise.

    Note
    ----
    This function uses `match_identical_names_except_missing_suffix` which
    may be incomplete in its current implementation.
    """
    return match_identical_names_except_missing_suffix(
        source_flows,
        target_flows,
        suffix="ion",
        comment="Match emissions with suffix ion",
    )
