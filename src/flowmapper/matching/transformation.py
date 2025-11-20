"""Transformation-based matching functions.

This module contains matching functions that apply transformations to flows
before matching.
"""

from collections.abc import Callable
from functools import partial

from randonneur import Datapackage

from flowmapper.domain import MatchCondition, NormalizedFlow
from flowmapper.matching.core import get_matches
from flowmapper.utils import FlowTransformationContext, apply_randonneur, toolz


def match_ecoinvent_transitive_matching(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list:
    """Match flows using ecoinvent transitive transformation.

    This function applies a transitive transformation that harmonizes flows
    from ecoinvent 2.2 to ecoinvent 3.12 biosphere, then matches flows with
    identical normalized names, context, and location after transformation.

    The transformation is applied to both source and target flows using
    FlowTransformationContext, which automatically resets flows to their
    normalized state after matching.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.close for flows that match
        after applying the ecoinvent transitive transformation.

    Notes
    -----
    - Uses the "ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive"
      transformation datapackage
    - Transforms both name and context fields
    - Names are compared case-insensitively after transformation
    - Match condition is MatchCondition.close (not exact due to transformation)
    - Flows are automatically reset to normalized state after matching
    - Only unit-compatible flows are matched
    """
    matches = []

    func: Callable[[list[NormalizedFlow]], list[NormalizedFlow]] = partial(
        apply_randonneur,
        datapackage="ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive",
        fields=["name", "context"],
    )

    with (
        FlowTransformationContext(source_flows, func) as sf,
        FlowTransformationContext(target_flows, func) as tf,
    ):
        for (name, context, location), sources in toolz.itertoolz.groupby(
            lambda x: (x.name, x.context, x.location), sf
        ).items():
            matches.extend(
                get_matches(
                    source_flows=sources,
                    target_flows=[
                        target
                        for target in tf
                        if target.name.lower() == name.lower()
                        and target.context == context
                        and target.location == location
                    ],
                    comment=f"Shared normalized name when transitively harmonized to ecoinvent 3.12 with identical context and location: {name}",
                    function_name="match_ecoinvent_transitive_matching",
                    match_condition=MatchCondition.close,
                )
            )

    return matches


def match_with_transformation(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    transformation: str | Datapackage | dict,
    fields: list[str],
    normalize: bool = True,
) -> list:
    """Match flows after applying a custom transformation.

    This function applies a specified transformation to source flows, then
    matches them to target flows based on the transformed attributes. The
    transformation is applied using FlowTransformationContext, which
    automatically resets flows to their normalized state after matching.

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against (not transformed).
    transformation : str
        Name or identifier of the transformation datapackage to apply.
    fields : list[str]
        List of field names to transform (e.g., ["name", "context"]).

    Returns
    -------
    list[Match]
        List of Match objects with MatchCondition.related for flows that match
        after applying the transformation to source flows.

    Notes
    -----
    - Transformation is only applied to source flows, not target flows
    - Transformed source flows are matched against original target flows
    - Match condition is MatchCondition.related (not exact due to transformation)
    - Flows are automatically reset to normalized state after matching
    - Only unit-compatible flows are matched

    Examples
    --------
    >>> matches = match_with_transformation(
    ...     source_flows=source_flows,
    ...     target_flows=target_flows,
    ...     transformation="ecoinvent-3.10-biosphere-simapro-2024-biosphere",
    ...     fields=["name"]
    ... )
    """
    matches = []

    func: Callable[[list[NormalizedFlow]], list[NormalizedFlow]] = partial(
        apply_randonneur,
        datapackage=transformation,
        fields=fields,
        normalize=normalize,
    )

    with FlowTransformationContext(source_flows, func) as sf:
        for (
            name,
            context,
            oxidation_state,
            location,
        ), sources in toolz.itertoolz.groupby(
            lambda x: (x.name, x.context, x.oxidation_state, x.location), sf
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
                    comment=f"Shared normalized attributes after applying transformation: {transformation}",
                    function_name="match_with_transformation",
                    match_condition=MatchCondition.related,
                )
            )

    return matches
