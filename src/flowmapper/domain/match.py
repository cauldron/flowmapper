"""Match class representing a mapping between source and target flows."""

from __future__ import annotations

from collections import UserString
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flowmapper.domain.flow import Flow
    from flowmapper.domain.match_condition import MatchCondition


@dataclass
class Match:
    """
    Represents a match between a source flow and a target flow.

    A Match object contains information about how a source flow maps to a target
    flow, including the match quality (condition), conversion factor, and metadata
    about how the match was found.

    Attributes
    ----------
    source : Flow
        The source flow being matched.
    target : Flow
        The target flow that the source maps to.
    function_name : str
        The name of the matching function that found this match.
    condition : MatchCondition
        The quality/type of the match (exact, close, related, etc.).
    conversion_factor : float, default=1.0
        The factor to convert from source unit to target unit.
    comment : str, default=""
        Optional comment describing the match.
    new_target_flow : bool, default=False
        Whether this match created a new target flow that didn't exist before.

    Examples
    --------
    >>> from flowmapper.domain.flow import Flow
    >>> from flowmapper.domain.match import Match
    >>> from flowmapper.domain.match_condition import MatchCondition
    >>> source = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> target = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> match = Match(
    ...     source=source,
    ...     target=target,
    ...     function_name="match_identical_names",
    ...     condition=MatchCondition.exact
    ... )
    >>> match.export()
    {'source': {...}, 'target': {...}, 'condition': '...', ...}
    """

    source: Flow
    target: Flow
    function_name: str
    condition: MatchCondition
    conversion_factor: float = 1.0
    comment: str = field(default_factory=lambda: "")
    new_target_flow: bool = False

    def export(self, flowmapper_metadata: bool = False) -> dict:
        """
        Export the match to a dictionary format.

        This method serializes the match to a dictionary suitable for JSON
        export or storage. The source and target flows are converted to
        dictionaries, and special objects are serialized appropriately.

        Parameters
        ----------
        flowmapper_metadata : bool, default=False
            If True, include flowmapper-specific metadata (version, function_name)
            in the export.

        Returns
        -------
        dict
            Dictionary containing the match data, with source and target as
            dictionaries and condition as a string URI.

        Examples
        --------
        >>> match.export()
        {'source': {...}, 'target': {...}, 'condition': '...', ...}
        >>> match.export(flowmapper_metadata=True)
        {'source': {...}, 'target': {...}, 'condition': '...', 'flowmapper_metadata': {...}, ...}
        """
        from flowmapper import __version__
        from flowmapper.fields import ContextField

        def serializable(obj: Any) -> Any:
            if isinstance(obj, UserString):
                return str(obj)
            elif isinstance(obj, ContextField):
                return obj.value
            return obj

        data = asdict(self)
        data["source"] = {
            k: serializable(v)
            for k, v in data["source"].items()
            if v and not k.startswith("_")
        }
        data["target"] = {
            k: serializable(v)
            for k, v in data["target"].items()
            if v and not k.startswith("_")
        }
        data["condition"] = str(data["condition"])

        function_name = data.pop("function_name")
        if flowmapper_metadata:
            data["flowmapper_metadata"] = {
                "version": __version__,
                "function_name": function_name,
            }

        return data

    def __lt__(self, other: Match) -> bool:
        """
        Compare matches for sorting.

        Matches are sorted by source name, source context, target name,
        and target context in that order.
        """
        return (
            self.source.name,
            self.source.context,
            self.target.name,
            self.target.context,
        ) < (
            other.source.name,
            other.source.context,
            other.target.name,
            other.target.context,
        )
