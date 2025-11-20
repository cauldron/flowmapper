"""Context-based matching functions.

This module contains matching functions that match flows based on context
relationships.
"""

from flowmapper.domain import MatchCondition, NormalizedFlow
from flowmapper.matching.core import get_matches
from flowmapper.utils import toolz


def match_resources_with_wrong_subcontext(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match resource flows ignoring subcontext differences.

    This function matches flows that are both resource-type flows (as
    determined by `context.is_resource()`), have identical names, oxidation
    states, and locations, but may have different subcontexts. This handles
    cases where resource flows are categorized differently but represent the
    same resource.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match. Only resource-type flows are considered.
    target_flows : list[NormalizedFlow]
        List of target flows to match against. Only resource-type flows are
        considered.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.close for resource flows
        with identical names, oxidation states, and locations, but potentially
        different subcontexts.

    Notes
    -----
    - Only flows where `normalized.context.is_resource()` returns True are matched
    - Name, oxidation state, and location must match exactly
    - Subcontext differences are ignored (both must be resource-type)
    - Match condition is MatchCondition.close (not exact due to subcontext differences)
    - Only unit-compatible flows are matched
    """
    matches = []

    for (name, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.oxidation_state, x.location),
        filter(lambda f: f.normalized.context.is_resource(), source_flows),
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name == name
                    and flow.normalized.context.is_resource()
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized name and resource-type context, with identical oxidation state and location: {name}",
                match_condition=MatchCondition.close,
                function_name="match_resources_with_wrong_subcontext",
            )
        )

    return matches


def match_name_and_parent_context(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows where target has parent context of source.

    This function matches flows where the source flow has a multi-level context
    (e.g., ["emissions", "to air"]) and the target flow has the parent context
    (e.g., ["emissions"]). This handles cases where flows are categorized at
    different levels of specificity.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match. Only flows with multi-level contexts
        (length > 1) are considered.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.related for flows where the
        target context is the parent of the source context.

    Notes
    -----
    - Only source flows with contexts of length > 1 are considered
    - Target context must exactly match the parent of source context (context[:-1])
    - Name, oxidation state, and location must match exactly
    - Match condition is MatchCondition.related (not exact due to context differences)
    - Only unit-compatible flows are matched

    Examples
    --------
    >>> # Source: context=["emissions", "to air"]
    >>> # Target: context=["emissions"]
    >>> # These will match if name, oxidation_state, and location also match
    """
    matches = []

    for (name, oxidation_state, context, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.oxidation_state, x.context, x.location),
        filter(lambda f: len(f.context) > 1, source_flows),
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name == name
                    and flow.context == context[:-1]
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment="Shared normalized name and parent context, with identical oxidation state and location",
                match_condition=MatchCondition.related,
                function_name="match_name_and_parent_context",
            )
        )

    return matches
