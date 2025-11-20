"""Core matching utilities.

This module contains core utility functions for matching flows, including
transformation and filtering support.
"""

import itertools
from collections.abc import Callable

from flowmapper.domain import Match, NormalizedFlow
from flowmapper.utils import FlowTransformationContext, apply_randonneur, toolz


def transform_and_then_match(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    match_function: Callable,
    transform_source_flows: Callable | None = None,
    transform_target_flows: Callable | None = None,
    filter_source_flows: Callable | None = None,
    filter_target_flows: Callable | None = None,
) -> list[Match]:
    """Apply transformations and filters to flows, then match them.

    This function provides a flexible way to apply transformations and filters
    to source and target flows before matching, while ensuring all flows are
    reset to their normalized state after matching completes.

    The function applies transformations and filters in the following order:
    1. Transform source flows (if provided)
    2. Filter source flows (if provided)
    3. Transform target flows (if provided)
    4. Filter target flows (if provided)
    5. Call match function with filtered flows
    6. Reset all flows to normalized state

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match.
    target_flows : list[NormalizedFlow]
        List of target flows to match against.
    match_function : Callable
        Function that performs the actual matching. Must accept keyword arguments
        `source_flows` and `target_flows` (both lists of NormalizedFlow) and return
        a list of Match objects.
    transform_source_flows : Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None
        Optional function to transform source flows. Takes a list of NormalizedFlow
        objects and returns a modified list. The function should modify flows in place
        (e.g., using update_current) and return the same list.
    transform_target_flows : Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None
        Optional function to transform target flows. Takes a list of NormalizedFlow
        objects and returns a modified list. The function should modify flows in place
        (e.g., using update_current) and return the same list.
    filter_source_flows : Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None
        Optional function to filter source flows. Takes a list of NormalizedFlow objects
        and returns a filtered list (may be shorter than input).
    filter_target_flows : Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None
        Optional function to filter target flows. Takes a list of NormalizedFlow objects
        and returns a filtered list (may be shorter than input).

    Returns
    -------
    list[Match]
        List of Match objects found by the match function.

    Examples
    --------
    >>> from flowmapper.matching import match_identical_names, transform_and_then_match
    >>> from flowmapper.utils import apply_randonneur
    >>> from functools import partial
    >>>
    >>> # Transform flows before matching
    >>> transform_func = partial(
    ...     apply_randonneur,
    ...     datapackage="some-transformation",
    ...     fields=["name", "context"]
    ... )
    >>>
    >>> matches = transform_and_then_match(
    ...     source_flows=source_flows,
    ...     target_flows=target_flows,
    ...     match_function=match_identical_names,
    ...     transform_source_flows=transform_func,
    ...     transform_target_flows=transform_func
    ... )
    >>>
    >>> # Filter flows before matching
    >>> def filter_resources(flows):
    ...     return [f for f in flows if f.normalized.context.is_resource()]
    >>>
    >>> matches = transform_and_then_match(
    ...     source_flows=source_flows,
    ...     target_flows=target_flows,
    ...     match_function=match_identical_names,
    ...     filter_source_flows=filter_resources,
    ...     filter_target_flows=filter_resources
    ... )

    Notes
    -----
    All flows (both source and target) are automatically reset to their normalized
    state after matching completes successfully. If the match function raises an
    exception, flows will not be reset.
    """
    transformed_source_flows = (
        transform_source_flows(source_flows) if transform_source_flows else source_flows
    )
    filtered_source_flows = (
        filter_source_flows(transformed_source_flows)
        if filter_source_flows
        else transformed_source_flows
    )

    transformed_target_flows = (
        transform_target_flows(target_flows) if transform_target_flows else target_flows
    )
    filtered_target_flows = (
        filter_target_flows(transformed_target_flows)
        if filter_target_flows
        else transformed_target_flows
    )

    matches = match_function(
        source_flows=filtered_source_flows, target_flows=filtered_target_flows
    )

    for flow in itertools.chain(source_flows, target_flows):
        flow.reset_current()

    return matches


def get_matches(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    comment: str,
    function_name: str,
    match_condition: "MatchCondition",
    conversion_factors: list[float] | None = None,
) -> list[Match]:
    """Create Match objects from source and target flows.

    This is a helper function used by various matching functions to create
    Match objects with proper unit compatibility checking and conversion
    factor calculation. It handles the common logic of:
    - Filtering target flows by unit compatibility
    - Resolving multiple target matches by context matching
    - Calculating conversion factors
    - Marking source flows as matched

    Parameters
    ----------
    source_flows : list[NormalizedFlow]
        List of source flows to match. Each source flow will be matched
        against compatible target flows.
    target_flows : list[NormalizedFlow]
        List of target flows to match against. Only unit-compatible flows
        are considered.
    comment : str
        Comment to include in each Match object describing the match.
    function_name : str
        Name of the matching function that created this match (e.g.,
        "match_identical_names").
    match_condition : MatchCondition
        The match quality condition (exact, close, related, etc.).
    conversion_factors : list[float] | None, optional
        Optional list of conversion factors, one per source flow. If None,
        conversion factors are calculated automatically. If provided, must
        have the same length as source_flows.

    Returns
    -------
    list[Match]
        List of Match objects. Each Match represents a successful match
        between a source flow and a target flow.

    Raises
    ------
    ValueError
        If conversion_factors is provided and its length doesn't match
        the length of source_flows.

    Notes
    -----
    - Only unit-compatible flows are matched (checked via `unit_compatible()`)
    - If multiple target flows are unit-compatible, the function tries to
      find the most appropriate match by matching normalized contexts
    - If exactly one target flow matches after context filtering, a Match
      is created and the source flow is marked as matched
    - Conversion factors are calculated automatically if not provided
    - The function only creates matches when there is exactly one target
      flow remaining after filtering

    Examples
    --------
    >>> matches = get_matches(
    ...     source_flows=[source_flow],
    ...     target_flows=[target_flow1, target_flow2],
    ...     comment="Shared identifier",
    ...     function_name="match_identical_identifier",
    ...     match_condition=MatchCondition.exact
    ... )
    """
    from flowmapper.domain import MatchCondition  # noqa: F401

    if not target_flows:
        return []

    matches = []

    # Providing conversion_factors only makes sense if there is a single target flow
    # Otherwise you have M-to-N problem
    if conversion_factors is None:
        cfs = itertools.repeat(None)
    else:
        if not len(conversion_factors) == len(source_flows):
            raise ValueError(
                f"`conversion_factors` (length {len(conversion_factors)}) must have same length as `source_flows` (length {len(source_flows)})"
            )
        cfs = conversion_factors

    for conversion_factor, source in zip(cfs, source_flows):
        targets = [flow for flow in target_flows if source.unit_compatible(flow)]
        if len(targets) > 1:
            # Try find most-appropriate match if more than one is present. Added because ecoinvent
            # deprecated most stratospheric emissions and redirected them to air, unspecified, so
            # now all air, unspecified emissions have multiple targets.
            targets = [
                target
                for target in targets
                if target.normalized.context == source.normalized.context
            ]
        if len(targets) == 1:
            target = target_flows[0]
            source.matched = True
            if conversion_factor is None:
                conversion_factor = source.conversion_factor(target)
            matches.append(
                Match(
                    source=source.original,
                    target=target.original,
                    function_name=function_name,
                    comment=comment or "",
                    condition=match_condition,
                    conversion_factor=conversion_factor,
                )
            )

    return matches
