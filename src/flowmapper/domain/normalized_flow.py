"""NormalizedFlow class for managing flow transformations and matching state."""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from flowmapper.domain.flow import Flow


@dataclass
class NormalizedFlow:
    """
    Represents a flow with its original, normalized, and current states.

    NormalizedFlow tracks a flow through its lifecycle:
    - `original`: The flow as it was initially created
    - `normalized`: The flow after normalization (standard form for matching)
    - `current`: The current state (can be modified for transformations)

    This class is used for matching flows where transformations may be temporarily
    applied to the `current` state, then reset back to `normalized`.

    Attributes
    ----------
    original : Flow
        The original flow as created from source data.
    normalized : Flow
        The normalized version of the flow (standard form).
    current : Flow
        The current state of the flow (can be modified).
    matched : bool, default=False
        Whether this flow has been matched to a target flow.

    Examples
    --------
    >>> from flowmapper.domain import Flow, NormalizedFlow
    >>> flow = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> normalized = flow.normalize()
    >>> nf = NormalizedFlow(
    ...     original=flow,
    ...     normalized=normalized,
    ...     current=copy(normalized)
    ... )
    >>> nf.update_current(name="Modified")
    >>> nf.reset_current()  # Reset to normalized state
    """

    original: Flow
    normalized: Flow
    current: Flow
    matched: bool = False

    @property
    def name(self) -> str:
        """Return the current flow's name."""
        return self.current.name.data

    @property
    def unit(self) -> str:
        """Return the current flow's unit."""
        return self.current.unit.data

    @property
    def context(self) -> str | list[str] | tuple[str]:
        """Return the current flow's context."""
        return self.current.context.value

    @property
    def identifier(self) -> str | None:
        """Return the current flow's identifier."""
        return self.current.identifier

    @property
    def location(self) -> str | None:
        """Return the current flow's location."""
        return self.current.location

    @property
    def oxidation_state(self) -> int | None:
        """Return the current flow's oxidation state value."""
        return (
            self.current.oxidation_state.value if self.current.oxidation_state else None
        )

    @property
    def cas_number(self) -> str | None:
        """Return the current flow's CAS number."""
        return self.current.cas_number.data if self.current.cas_number else None

    @property
    def synonyms(self) -> list[str] | None:
        """Return the current flow's synonyms."""
        return self.current.synonyms

    def reset_current(self) -> None:
        """
        Reset the current flow to the normalized state.

        This method creates a copy of the normalized flow and sets it as the
        current flow. Useful after applying temporary transformations.
        """
        self.current = copy(self.normalized)

    def update_current(self, **kwargs) -> None:
        """
        Update the current flow with new attribute values.

        This method creates a new Flow based on the normalized flow's data,
        updated with the provided keyword arguments. The normalized flow
        remains unchanged.

        Parameters
        ----------
        **kwargs
            Keyword arguments corresponding to Flow attributes (name, unit,
            context, location, etc.).

        Examples
        --------
        >>> nf.update_current(name="Modified name", unit="g")
        """
        from flowmapper.domain.flow import Flow

        data = self.normalized.to_dict()
        data.update(kwargs)
        self.current = Flow.from_dict(data)

    @staticmethod
    def from_dict(data: dict) -> "NormalizedFlow":
        """
        Create a NormalizedFlow from a dictionary.

        This method creates the original flow, normalizes it, and sets up
        the NormalizedFlow with all three states.

        Parameters
        ----------
        data : dict
            Dictionary containing flow data.

        Returns
        -------
        NormalizedFlow
            A new NormalizedFlow instance.
        """
        from flowmapper.domain.flow import Flow

        original = Flow.from_dict(data)
        # Do data preprocessing here
        normalized = original.normalize()
        return NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

    def unit_compatible(self, other: Self) -> bool:
        """
        Check if this flow's unit is compatible with another flow's unit.

        Parameters
        ----------
        other : NormalizedFlow
            Another NormalizedFlow to compare units with.

        Returns
        -------
        bool
            True if the units are compatible (can be converted), False otherwise.
        """
        return self.current.unit.compatible(other.current.unit)

    def conversion_factor(self, other: Self) -> float:
        """
        Calculate the conversion factor from this flow's unit to another flow's unit.

        Parameters
        ----------
        other : NormalizedFlow
            Another NormalizedFlow to convert to.

        Returns
        -------
        float
            The conversion factor to multiply this flow's value by to get the
            equivalent value in the other flow's unit.
        """
        return self.current.unit.conversion_factor(other.current.unit)

    def export(self) -> dict:
        """
        Export the flow data for serialization.

        Returns a dictionary containing the original flow's data, suitable
        for JSON serialization or export to external formats.

        Returns
        -------
        dict
            Dictionary containing flow data with only non-None values.
        """
        data = [
            ("name", self.original.name.data),
            ("unit", self.original.unit.data),
            ("context", self.original.context.value),
            ("identifier", self.original.identifier),
            ("location", self.original.location),
            (
                "cas_number",
                (
                    self.normalized.cas_number.export()
                    if self.normalized.cas_number
                    else None
                ),
            ),
        ]
        return {k: v for k, v in data if v}

    def __repr__(self) -> str:
        """Return a string representation showing non-None attributes of original and current."""
        return f"""NormalizedFlow(
    original={self.original!r}
    current={self.current!r}
    matched={self.matched!r}
)"""
