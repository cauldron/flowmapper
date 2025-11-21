"""Specialized matching functions.

This module contains specialized matching functions for specific use cases
like regionalized flows and suffix matching.
"""

from flowmapper.domain.match import Match
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.utils import toolz


def add_missing_regionalized_flows(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    function_name: str | None = None,
    comment: str | None = None,
    match_condition: MatchCondition | None = None,
) -> list[Match]:
    """Add missing regionalized flows based on existing regionalized flows.

    If a source flow has a location and there are target flows with the same
    name, context, and oxidation state but different locations, create a new
    target flow for the source location.

    The function groups source flows by (name, oxidation_state, context, location)
    and for each group:
    - If there are other regionalized target flows (same name/context/oxidation_state
      but different location), uses the first one as a template
    - Otherwise, if there is exactly one non-regionalized target flow (same
      name/context/oxidation_state but no location), uses that as a template
    - Creates a new target flow by copying the template and setting the source's
      location using `copy_with_new_location`

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match. Only flows with a location are considered.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.
    function_name : str | None, optional
        Name of the matching function (currently not used, defaults to
        "add_missing_regionalized_flows").
    comment : str | None, optional
        Comment for matches (currently not used, defaults to a description of
        the new target flow).
    match_condition : MatchCondition | None, optional
        Match condition (currently not used, defaults to MatchCondition.related).

    Returns
    -------
    list[Match]
        List of Match objects with new_target_flow=True. Each match represents
        a source flow matched to a newly created target flow.

    Notes
    -----
    - Only source flows with a location are considered
    - Target flows must be unit-compatible with source flows to create matches
    - The new target flow is created using `copy_with_new_location`, which sets
      a new UUID identifier
    - All matches are created with `MatchCondition.related` and
      `new_target_flow=True`

    Examples
    --------
    >>> source = NormalizedFlow.from_dict({
    ...     "name": "Carbon dioxide, NL",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> target = NormalizedFlow.from_dict({
    ...     "name": "Carbon dioxide, DE",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> matches = add_missing_regionalized_flows(
    ...     source_flows=[source],
    ...     target_flows=[target]
    ... )
    >>> len(matches)
    1
    >>> matches[0].new_target_flow
    True
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
        non_regionalized = [
            flow
            for flow in target_flows
            if flow.name == name
            and flow.context == context
            and flow.oxidation_state == oxidation_state
            and flow.location is None
        ]

        if other_regions:
            target = other_regions[0]

            for source in sources:
                if source.unit_compatible(target):
                    source.matched = True
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
        elif len(non_regionalized) == 1:
            target = non_regionalized[0]

            for source in sources:
                if source.unit_compatible(target):
                    source.matched = True
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


def equivalent_names(a: str, b: str) -> bool:
    """Check if two flow names are equivalent after removing certain suffixes.

    This function determines if two flow names represent the same substance by
    checking if they differ only by specific suffixes that don't change the
    fundamental identity of the flow. It handles two types of equivalences:

    1. **Suffix removal**: Names are equivalent if one has a suffix and the
       other doesn't, but the base names match. Supported suffixes:
       - ", in ground"
       - ", ion"
       - ", in air"
       - ", in water"
       - ", unspecified origin"

    2. **Biogenic/non-fossil equivalence**: Names ending with ", biogenic" and
       ", non-fossil" are considered equivalent if the base names match.

    Parameters
    ----------
    a : str
        First flow name to compare.
    b : str
        Second flow name to compare.

    Returns
    -------
    bool
        True if the names are equivalent (differ only by supported suffixes),
        False otherwise.

    Notes
    -----
    - The function is case-sensitive for the base name comparison
    - Suffix matching is exact (must match the full suffix string)
    - For biogenic/non-fossil equivalence, the base names must match exactly
      after removing the respective suffixes (10 chars for ", biogenic" and
      12 chars for ", non-fossil")
    - The ", ion" suffix is safe to ignore because matching functions also
      check for matching oxidation states, ensuring correct matching

    Examples
    --------
    >>> equivalent_names("Carbon dioxide, in air", "Carbon dioxide")
    True
    >>> equivalent_names("Carbon dioxide", "Carbon dioxide, in air")
    True
    >>> equivalent_names("Carbon dioxide, in ground", "Carbon dioxide, in air")
    False
    >>> equivalent_names("Methane, biogenic", "Methane, non-fossil")
    True
    >>> equivalent_names("Carbon dioxide, ion", "Carbon dioxide")
    True
    >>> equivalent_names("Carbon dioxide", "Carbon monoxide")
    False
    """
    suffixes = [
        ", in ground",
        ", ion",  # OK because we still check for single match and matching oxidation state
        ", in air",
        ", in water",
        ", unspecified origin",
    ]
    for suffix in suffixes:
        if a.endswith(suffix) and not b.endswith(suffix) and a[: -len(suffix)] == b:
            return True
        if b.endswith(suffix) and not a.endswith(suffix) and b[: -len(suffix)] == a:
            return True
    if a.endswith(", biogenic") and b.endswith(", non-fossil") and a[:-10] == b[:-12]:
        return True
    if b.endswith(", biogenic") and a.endswith(", non-fossil") and b[:-10] == a[:-12]:
        return True
    return False


def match_names_with_suffix_removal(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    function_name: str | None = None,
    comment: str | None = None,
    match_condition: MatchCondition | None = None,
) -> list[Match]:
    """Match flows where names are equivalent after removing certain suffixes.

    This function matches source and target flows where the names are considered
    equivalent by `equivalent_names`, meaning they differ only by supported
    suffixes (e.g., ", in air", ", in ground", ", ion", ", biogenic"/", non-fossil").
    In addition to name equivalence, flows must also have matching:
    - Context
    - Oxidation state
    - Location

    The function groups source flows by (name, context, oxidation_state, location)
    and for each group, finds target flows with equivalent names (using
    `equivalent_names`) and matching attributes.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match. Flows are grouped by name, context,
        oxidation state, and location.
    target_flows : list[NormalizedFlow]
        List of target flows to match against. Only flows with equivalent names
        and matching attributes are considered.
    function_name : str | None, optional
        Name of the matching function. Defaults to "match_names_with_suffix_removal".
    comment : str | None, optional
        Comment for matches. Defaults to a descriptive string about suffix removal.
    match_condition : MatchCondition | None, optional
        The match quality condition. Defaults to MatchCondition.close.

    Returns
    -------
    list[Match]
        List of Match objects representing successful matches. Each match has
        a source flow and target flow with equivalent names (after suffix removal)
        and matching context, oxidation state, and location.

    Notes
    -----
    - Names are compared in lowercase for matching
    - Only unit-compatible flows are matched (handled by `get_matches`)
    - The function uses `equivalent_names` to determine name equivalence
    - Supported suffixes include: ", in ground", ", ion", ", in air", ", in water",
      ", unspecified origin", and the biogenic/non-fossil pair
    - If multiple target flows match, `get_matches` handles resolution based on
      context matching

    Examples
    --------
    >>> from flowmapper.domain.normalized_flow import NormalizedFlow
    >>> from flowmapper.matching.specialized import match_names_with_suffix_removal
    >>>
    >>> source = NormalizedFlow.from_dict({
    ...     "name": "Carbon dioxide, in air",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> target = NormalizedFlow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> matches = match_names_with_suffix_removal(
    ...     source_flows=[source],
    ...     target_flows=[target]
    ... )
    >>> len(matches)
    1
    >>> matches[0].condition
    MatchCondition.close
    """
    from flowmapper.matching.core import get_matches

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
                    if equivalent_names(name, flow.name.lower())
                    and flow.context == context
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=comment
                or f"Shared normalized lowercase name with suffix removed and identical context, oxidation state, and location: {name}",
                function_name=function_name or "match_names_with_suffix_removal",
                match_condition=match_condition or MatchCondition.close,
            )
        )

    return matches
