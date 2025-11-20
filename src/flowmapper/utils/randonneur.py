"""Randonneur-based transformation utility functions."""

from __future__ import annotations

import copy
from collections.abc import Callable
from contextlib import AbstractContextManager
from functools import partial
from typing import TYPE_CHECKING, Any

from randonneur import Datapackage, MigrationConfig, migrate_nodes
from randonneur_data import Registry

from flowmapper.utils.constants import default_registry
from flowmapper.utils.context import tupleize_context

if TYPE_CHECKING:
    from flowmapper.domain import Flow, NormalizedFlow


def randonneur_as_function(
    datapackage: str | Datapackage | dict,
    fields: list[str] | None = None,
    registry: Registry | None = None,
    verbs: list[str] | None = None,
) -> Callable:
    """Take a prepared transformation in"""
    if registry is None:
        registry = default_registry
    if verbs is None:
        verbs = ["update"]

    if isinstance(datapackage, Datapackage):
        datapackage = datapackage.data
    elif isinstance(datapackage, str):
        datapackage = registry.get_file(datapackage)
    elif "update" not in datapackage:
        raise KeyError

    return partial(
        migrate_nodes,
        migrations=tupleize_context(datapackage),
        config=MigrationConfig(
            verbs=verbs,
            case_sensitive=(
                False
                if "case-insensitive" not in datapackage
                else not datapackage.get("case-insensitive")
            ),
            fields=fields,
        ),
    )


def apply_randonneur(
    flows: list[NormalizedFlow],
    datapackage: str | Datapackage | dict,
    fields: list[str] | None = None,
    registry: Registry | None = None,
) -> list[NormalizedFlow]:
    """Apply randonneur transformations to NormalizedFlow objects."""
    from flowmapper.domain import Flow

    func = randonneur_as_function(
        datapackage=datapackage, fields=fields, registry=registry
    )
    transformed_data = func(graph=[nf.normalized.to_dict() for nf in flows])

    for flow, data_dict in zip(flows, transformed_data):
        flow.current = Flow.from_dict(data_dict)

    return flows


def apply_generic_transformations_to_flows(
    functions: list[Callable[..., list[NormalizedFlow]]], flows: list[Flow]
) -> list[NormalizedFlow]:
    """
    Apply a series of transformation functions to flows and return NormalizedFlow objects.

    This function takes a list of Flow objects and applies a sequence of transformation
    functions to them. Each transformation function receives the flow data as dictionaries
    (via the `graph` keyword argument) and returns modified dictionaries. The transformations
    are applied sequentially, with each function receiving the output of the previous one.

    After all transformations are applied, the modified flow dictionaries are converted back
    to Flow objects, normalized, and wrapped in NormalizedFlow objects. The original Flow
    objects are preserved and stored in the `original` attribute of each NormalizedFlow.

    Parameters
    ----------
    functions : list[Callable[..., list[dict]]]
        List of transformation functions to apply sequentially. Each function must accept
        a `graph` keyword argument containing a list of flow dictionaries and return a
        list of modified flow dictionaries. Functions are typically created using
        `randonneur_as_function()`.
    flows : list[Flow]
        List of Flow objects to transform. The original Flow objects are not modified.

    Returns
    -------
    list[NormalizedFlow]
        List of NormalizedFlow objects, one for each input flow. Each NormalizedFlow contains:
        - `original`: The original Flow object (unchanged)
        - `normalized`: The transformed and normalized Flow object
        - `current`: A copy of the normalized Flow object

    Examples
    --------
    >>> from flowmapper.domain import Flow
    >>> from flowmapper.utils import apply_generic_transformations_to_flows, randonneur_as_function
    >>>
    >>> # Create a transformation function
    >>> transform_func = randonneur_as_function(datapackage="some-transformation")
    >>>
    >>> # Create flows
    >>> flows = [
    ...     Flow.from_dict({"name": "Carbon dioxide", "context": "air", "unit": "kg"})
    ... ]
    >>>
    >>> # Apply transformations
    >>> normalized_flows = apply_generic_transformations_to_flows(
    ...     functions=[transform_func],
    ...     flows=flows
    ... )
    >>>
    >>> # Access transformed data
    >>> print(normalized_flows[0].normalized.name.data)
    """
    from flowmapper.domain import Flow, NormalizedFlow

    flow_dicts = [obj.to_dict() for obj in flows]

    for function in functions:
        flow_dicts = function(graph=flow_dicts)

    normalized_flows = [Flow.from_dict(obj).normalize() for obj in flow_dicts]

    return [
        NormalizedFlow(original=o, normalized=n, current=copy.copy(n))
        for o, n in zip(flows, normalized_flows)
    ]


class FlowTransformationContext(AbstractContextManager):
    """
    Context manager that applies a function to NormalizedFlows on entry and resets them on exit.

    This context manager is useful when you need to temporarily modify flows for matching
    or processing, and want to ensure they are reset to their normalized state afterward.

    Parameters
    ----------
    flows : list[NormalizedFlow]
        List of NormalizedFlow objects to transform and reset.
    function : Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None
        Function to apply to the flows on context entry. The function should take
        a list of NormalizedFlow objects and return the modified list. If None,
        no transformation is applied.

    Examples
    --------
    >>> flows = [NormalizedFlow(...), NormalizedFlow(...)]
    >>> def update_func(flows):
    ...     for flow in flows:
    ...         flow.update_current(name="Modified")
    ...     return flows
    >>> with FlowTransformationContext(flows, update_func) as modified_flows:
    ...     # modified_flows contains the transformed flows
    ...     do_something_with(modified_flows)
    >>> # flows are automatically reset to normalized state
    """

    def __init__(
        self,
        flows: list[NormalizedFlow],
        function: Callable[[list[NormalizedFlow]], list[NormalizedFlow]] | None = None,
    ):
        self.flows = flows
        self.function = function

    def __enter__(self) -> list[NormalizedFlow]:
        """Apply the function to the flows on entry."""
        if self.function is not None:
            self.flows = self.function(self.flows)
        return self.flows

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Reset all flows to their normalized state on exit."""
        for flow in self.flows:
            flow.reset_current()
