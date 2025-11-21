"""Flow class representing an elementary flow with all its attributes."""

import itertools
import uuid
from dataclasses import dataclass, field
from typing import Any, Self

from flowmapper.errors import MissingLocation
from flowmapper.fields import (
    CASField,
    ContextField,
    OxidationState,
    StringField,
    replace_location_suffix,
    split_location_suffix,
)
from flowmapper.unit import UnitField
from flowmapper.utils import remove_unit_slash

global_counter = itertools.count(0)


@dataclass(frozen=True)
class Flow:
    """
    Represents an elementary flow with all its attributes.

    A Flow is an immutable dataclass that represents an elementary flow (e.g., a substance
    or material) with its name, unit, context, and optional attributes like location,
    CAS number, and synonyms. Flows can be normalized to a standard form for matching
    and comparison.

    Attributes
    ----------
    name : StringField
        The name of the flow (e.g., "Carbon dioxide").
    unit : UnitField
        The unit of measurement (e.g., "kg", "m3").
    context : ContextField
        The context or category of the flow (e.g., "air", "water").
    identifier : str | None, optional
        An optional unique identifier for the flow.
    location : str | None, optional
        An optional location code (e.g., "NL", "DE", "US").
    oxidation_state : OxidationState | None, optional
        The oxidation state of the flow if applicable.
    cas_number : CASField | None, optional
        The CAS (Chemical Abstracts Service) registry number.
    synonyms : list[str], default=[]
        A list of alternative names for the flow.
    _id : int
        Internal unique identifier (auto-generated).

    Examples
    --------
    >>> flow = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> normalized = flow.normalize()
    >>> print(normalized.name.data)
    carbon dioxide
    """

    name: StringField
    unit: UnitField
    context: ContextField
    identifier: str | None = None  # Internal ID, not necessarily present or unique...
    location: str | None = None
    oxidation_state: OxidationState | None = None
    cas_number: CASField | None = None
    synonyms: list[str] = field(default_factory=lambda: [])
    conversion_factor: float | None = None
    _id: int = field(default_factory=lambda: next(global_counter))

    @staticmethod
    def randonneur_mapping() -> dict:
        """
        Return the randonneur mapping configuration for Flow objects.

        Returns
        -------
        dict
            A dictionary containing JSONPath expressions for mapping Flow attributes
            to randonneur transformation format.
        """
        return {
            "expression language": "JSONPath",
            "labels": {
                "unit": "$.unit",
                "name": "$.name",
                "context": "$.context",
                "identifier": "$.identifier",
                "location": "$.location",
                "cas_number": "$.cas_number",
                "synonyms": "$.synonyms",
                "conversion_factor": "$.conversion_factor",
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Create a Flow instance from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing flow data with keys: name, unit, context, and
            optionally identifier, location, oxidation_state, cas_number, synonyms.

        Returns
        -------
        Flow
            A new Flow instance created from the dictionary data.

        Examples
        --------
        >>> flow = Flow.from_dict({
        ...     "name": "Carbon dioxide",
        ...     "context": "air",
        ...     "unit": "kg",
        ...     "location": "NL"
        ... })
        """
        return cls(
            name=StringField(data["name"]),
            unit=UnitField(data["unit"]),
            context=ContextField(data["context"]),
            identifier=data.get("identifier"),
            location=data.get("location") or None,
            oxidation_state=(
                OxidationState(data["oxidation_state"])
                if data.get("oxidation_state")
                else None
            ),
            cas_number=CASField.from_string(data.get("cas_number") or None),
            synonyms=data.get("synonyms") or [],
            conversion_factor=data.get("conversion_factor"),
        )

    def to_dict(self) -> dict:
        """
        Convert the Flow to a dictionary representation.

        Returns
        -------
        dict
            Dictionary containing the flow's data. Only non-None optional fields
            are included.

        Examples
        --------
        >>> flow = Flow.from_dict({"name": "CO2", "context": "air", "unit": "kg"})
        >>> flow.to_dict()
        {'name': 'CO2', 'unit': 'kg', 'context': ('air',), 'identifier': None}
        """
        data = {
            "name": self.name.data,
            "unit": self.unit.data,
            "context": self.context.as_tuple(),
            "identifier": self.identifier,
        }
        for key in (
            "location",
            "oxidation_state",
            "cas_number",
            "synonyms",
            "conversion_factor",
        ):
            if getattr(self, key):
                data[key] = getattr(self, key)
        return data

    def normalize(self) -> Self:
        """
        Normalize the flow to a standard form for matching.

        This method performs several normalization steps:
        1. Removes unit references from the name (e.g., "/kg")
        2. Extracts location from the name suffix (e.g., ", NL")
        3. Extracts oxidation state from the name (e.g., "Iron(II)")
        4. Normalizes the name, unit, and context fields

        Returns
        -------
        Flow
            A new Flow instance with normalized attributes.

        Examples
        --------
        >>> flow = Flow.from_dict({
        ...     "name": "Carbon dioxide, NL",
        ...     "context": "air",
        ...     "unit": "kg"
        ... })
        >>> normalized = flow.normalize()
        >>> normalized.location
        'NL'
        """
        location, oxidation_state = self.location, self.oxidation_state
        name = remove_unit_slash(self)
        name, other_location = split_location_suffix(name)
        if other_location:
            location = other_location
        if OxidationState.has_oxidation_state(name):
            oxidation_state, name = OxidationState.from_string(name)

        return type(self)(
            identifier=self.identifier,
            name=StringField(name).normalize(),
            location=location,
            oxidation_state=oxidation_state,
            unit=self.unit.normalize(),
            context=self.context.normalize(),
            cas_number=self.cas_number,
            synonyms=self.synonyms,
            conversion_factor=self.conversion_factor,
        )

    def copy_with_new_location(self, location: str) -> Self:
        """
        Create a copy of the flow with a new location in the name.

        This method replaces the location suffix in the flow's name with a new
        location value. If no location suffix is found, it appends the location
        to the name. The original flow is not modified.

        The new flow will have a new UUID identifier, regardless of whether
        the original flow had an identifier.

        Parameters
        ----------
        location : str
            The new location code to use (e.g., "DE", "FR").

        Returns
        -------
        Flow
            A new Flow instance with the updated location in the name and a new
            UUID identifier.

        Notes
        -----
        - If the flow's name contains a location suffix (matched by the
          ends_with_location regex), it is replaced with the new location.
        - If no location suffix is found, the location is appended to the name
          in the format ", <location>".
        - The new flow always gets a new UUID identifier via `uuid.uuid4()`.

        Examples
        --------
        >>> flow = Flow.from_dict({
        ...     "name": "Carbon dioxide, NL",
        ...     "context": "air",
        ...     "unit": "kg"
        ... })
        >>> new_flow = flow.copy_with_new_location("DE")
        >>> new_flow.name.data
        'Carbon dioxide, DE'
        >>> new_flow.identifier != flow.identifier
        True
        >>> # If no location suffix exists, location is appended
        >>> flow2 = Flow.from_dict({
        ...     "name": "Carbon dioxide",
        ...     "context": "air",
        ...     "unit": "kg"
        ... })
        >>> new_flow2 = flow2.copy_with_new_location("DE")
        >>> new_flow2.name.data
        'Carbon dioxide, DE'
        """
        if not location:
            raise ValueError("No location parameter given")

        data = self.to_dict()
        try:
            data["name"] = replace_location_suffix(
                string=data["name"], new_location=location
            )
        except MissingLocation:
            data["name"] = (
                data["name"].strip()
                + (", " if not data["name"].endswith(",") else " ")
                + location
            )
        data["identifier"] = str(uuid.uuid4())
        return type(self).from_dict(data)

    def __repr__(self) -> str:
        """Return a string representation showing all non-None attributes."""
        parts = [
            f"name={self.name!r}",
            f"unit={self.unit!r}",
            f"context={self.context!r}",
        ]
        if self.identifier is not None:
            parts.append(f"identifier={self.identifier!r}")
        if self.location is not None:
            parts.append(f"location={self.location!r}")
        if self.oxidation_state is not None:
            parts.append(f"oxidation_state={self.oxidation_state!r}")
        if self.cas_number is not None:
            parts.append(f"cas_number={self.cas_number!r}")
        if self.synonyms:
            parts.append(f"synonyms={self.synonyms!r}")
        if self.conversion_factor:
            parts.append(f"conversion_factor={self.conversion_factor!r}")
        return f"Flow({', '.join(parts)})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on internal _id."""
        if not isinstance(other, Flow):
            return False
        return self._id == other._id

    def __lt__(self, other: Self) -> bool:
        """
        Compare flows for sorting.

        Flows are compared by name, unit, context, and identifier in that order.
        """
        if not isinstance(other, Flow):
            return False
        else:
            return (
                self.name.data,
                self.unit.data,
                self.context.value,
                self.identifier,
            ) < (
                other.name.data,
                other.unit.data,
                other.context.value,
                other.identifier,
            )
