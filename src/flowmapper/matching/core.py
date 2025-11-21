"""Core matching utilities.

This module contains core utility functions for matching flows, including
transformation and filtering support.
"""

import itertools
from collections.abc import Callable

from flowmapper.domain.match import Match
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow


def transform_and_then_match(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    match_function: Callable,
    transform_source_flows: list[Callable] | None = None,
    transform_target_flows: list[Callable] | None = None,
    filter_source_flows: Callable | None = None,
    filter_target_flows: Callable | None = None,
) -> list[Match]:
    """Apply transformations and filters to flows, then match them.

    This function provides a flexible way to apply transformations and filters
    to source and target flows before matching, while ensuring all flows are
    reset to their normalized state after matching completes.

    The function applies transformations and filters in the following order:
    1. Transform source flows (if provided) - applies all transformations in sequence
    2. Filter source flows (if provided)
    3. Transform target flows (if provided) - applies all transformations in sequence
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
    transform_source_flows : list[Callable[[list[NormalizedFlow]], list[NormalizedFlow]]] | None
        Optional list of functions to transform source flows. Functions are applied
        in sequence. Each function takes a list of NormalizedFlow objects and returns
        a modified list. Functions should modify flows in place (e.g., using
        update_current) and return the same list.
    transform_target_flows : list[Callable[[list[NormalizedFlow]], list[NormalizedFlow]]] | None
        Optional list of functions to transform target flows. Functions are applied
        in sequence. Each function takes a list of NormalizedFlow objects and returns
        a modified list. Functions should modify flows in place (e.g., using
        update_current) and return the same list.
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
    >>> # Transform flows with a single function (wrap in list)
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
    ...     transform_source_flows=[transform_func],
    ...     transform_target_flows=[transform_func]
    ... )
    >>>
    >>> # Transform flows with multiple functions in sequence
    >>> transform1 = partial(apply_randonneur, datapackage="transformation-1", fields=["name"])
    >>> transform2 = partial(apply_randonneur, datapackage="transformation-2", fields=["context"])
    >>>
    >>> matches = transform_and_then_match(
    ...     source_flows=source_flows,
    ...     target_flows=target_flows,
    ...     match_function=match_identical_names,
    ...     transform_source_flows=[transform1, transform2],
    ...     transform_target_flows=[transform1, transform2]
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
    - All flows (both source and target) are automatically reset to their normalized
      state after matching completes successfully. If the match function raises an
      exception, flows will not be reset.
    - When multiple transformations are provided in a list, they are applied in
      sequence. The output of each transformation becomes the input to the next.
    - To apply a single transformation, wrap it in a list: `[transform_func]`
    """
    # Apply source flow transformations
    if transform_source_flows is None:
        transformed_source_flows = source_flows
    else:
        # Apply multiple transformations in sequence
        transformed_source_flows = source_flows
        for transform_func in transform_source_flows:
            transformed_source_flows = transform_func(transformed_source_flows)

    # Apply source flow filters
    filtered_source_flows = (
        filter_source_flows(transformed_source_flows)
        if filter_source_flows
        else transformed_source_flows
    )

    # Apply target flow transformations
    if transform_target_flows is None:
        transformed_target_flows = target_flows
    else:
        # Apply multiple transformations in sequence
        transformed_target_flows = target_flows
        for transform_func in transform_target_flows:
            transformed_target_flows = transform_func(transformed_target_flows)

    # Apply target flow filters
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
    match_condition: MatchCondition,
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

    Returns
    -------
    list[Match]
        List of Match objects. Each Match represents a successful match
        between a source flow and a target flow.

    Notes
    -----
    - Only unit-compatible flows are matched (checked via `unit_compatible()`)
    - If multiple target flows are unit-compatible, the function tries to
      find the most appropriate match by matching normalized contexts
    - If exactly one target flow matches after context filtering, a Match
      is created and the source flow is marked as matched
    - Conversion factors are calculated automatically using
      `source.conversion_factor(target)` which accounts for both unit
      conversion and any transformation factors
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
    if not target_flows:
        return []

    matches = []

    for source in source_flows:
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
            matches.append(
                Match(
                    source=source.original,
                    target=target.original,
                    function_name=function_name,
                    comment=comment or "",
                    condition=match_condition,
                    conversion_factor=source.conversion_factor(target),
                )
            )

    return matches
