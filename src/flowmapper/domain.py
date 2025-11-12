import itertools
from copy import copy
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Self

from flowmapper.cas import CASField
from flowmapper.context import ContextField
from flowmapper.location import split_location_suffix
from flowmapper.oxidation_state import OxidationState
from flowmapper.string_field import StringField
from flowmapper.unit import UnitField
from flowmapper.utils import remove_unit_slash

global_counter = itertools.count(0)


@dataclass(frozen=True)
class Flow:
    name: StringField
    unit: UnitField
    context: ContextField
    identifier: str | None = None  # Internal ID, not necessarily present or unique...
    location: str | None = None
    oxidation_state: OxidationState | None = None
    cas_number: CASField | None = None
    synonyms: list[str] = field(default_factory=lambda: [])
    _id: int = field(default_factory=lambda: next(global_counter))

    @staticmethod
    def randonneur_mapping() -> dict:
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
            }
        }


    @classmethod
    def from_dict(cls, data: dict) -> Self:
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
            cas_number=CASField.from_string(data.get("cas_number")),
            synonyms=data.get("synonyms") or [],
        )

    def to_dict(self) -> dict:
        data = {
            "name": self.name.data,
            "unit": self.unit.data,
            "context": self.context.as_tuple(),
            "identifier": self.identifier,
        }
        for key in ("location", "oxidation_state", "cas_number", "synonyms"):
            if getattr(self, key):
                data[key] = getattr(self, key)
        return data

    def normalize(self) -> Self:
        location, oxidation_state = None, None
        name = remove_unit_slash(self)
        name, location = split_location_suffix(name)
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
        )

    def __repr__(self) -> str:
        return f"""Flow dataclass:
    Identifier: {self.identifier}
    Name: {self.name}
    Context: {self.context}
    Unit: {self.unit}"""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Flow):
            return False
        return self._id == other._id

    def __lt__(self, other: Self) -> bool:
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


@dataclass
class NormalizedFlow:
    original: Flow
    normalized: Flow
    current: Flow
    matched: bool = False

    @property
    def name(self) -> str:
        return self.current.name.data

    @property
    def unit(self) -> str:
        return self.current.unit.data

    @property
    def context(self) -> str | list[str] | tuple[str]:
        return self.current.context.value

    @property
    def identifier(self) -> str | None:
        return self.current.identifier

    @property
    def location(self) -> str | None:
        return self.current.location

    @property
    def oxidation_state(self) -> int | None:
        return self.current.oxidation_state.value if self.current.oxidation_state else None

    @property
    def cas_number(self) -> str | None:
        return self.current.cas_number.data if self.current.cas_number else None

    @property
    def synonyms(self) -> list[str] | None:
        return self.current.synonyms

    def reset_current(self) -> None:
        self.current = copy(self.normalized)

    def update_current(self, **kwargs) -> None:
        data = self.normalized.to_dict()
        data.update(kwargs)
        self.current = Flow.from_dict(data)

    @staticmethod
    def from_dict(data: dict, transformations: list) -> "NormalizedFlow":
        original = Flow.from_dict(data)
        # Do data preprocessing here
        normalized = original.normalize()
        return NormalizedFlow(
            original=original, normalized=normalized, current=copy(normalized)
        )

    def unit_compatible(self, other: Self) -> bool:
        return self.current.unit.compatible(other.current.unit)

    def conversion_factor(self, other: Self) -> float:
        return self.current.unit.conversion_factor(other.current.unit)

    def export(self) -> dict:
        data = [
            ("name", self.original.name.data),
            ("unit", self.original.unit.data),
            ("context", self.original.context.value),
            ("identifier", self.original.identifier),
            ("location", self.original.location),
            (
                "cas_number",
                self.normalized.cas_number.export() if self.normalized.cas_number else None,
            ),
        ]
        return {k: v for k, v in data if v}


class MatchCondition(StrEnum):
    exact = "http://www.w3.org/2004/02/skos/core#exactMatch"
    close = "http://www.w3.org/2004/02/skos/core#closeMatch"
    # A triple <A> skos:broader <B> asserts that <B>, the object of the triple, is a broader concept
    # than <A>, the subject of the triple.
    narrow = "http://www.w3.org/2004/02/skos/core#narrowMatch"  # in SKOS the *target* is narrower than the *source*
    broad = "http://www.w3.org/2004/02/skos/core#broadMatch"  # in SKOS the *target* is broader than the *source*

    def as_glad(self) -> str:
        if self.value == "http://www.w3.org/2004/02/skos/core#exactMatch":
            return "="
        elif self.value == "http://www.w3.org/2004/02/skos/core#closeMatch":
            return "~"
        elif self.value == "http://www.w3.org/2004/02/skos/core#narrowMatch":
            return ">"
        elif self.value == "http://www.w3.org/2004/02/skos/core#broadMatch":
            return "<"
        raise ValueError  # Just for silly type checking


@dataclass
class Match:
    source: Flow
    target: Flow
    function_name: str
    condition: MatchCondition
    conversion_factor: float = 1.0
    comment: str = field(default_factory=lambda: "")

    def export(self, flowmapper_metadata: bool = False) -> dict:
        from flowmapper import __version__

        data = asdict(self)
        data["source"] = {
            k: v for k, v in data["source"].items() if v and not k.startswith("_")
        }
        data["target"] = {
            k: v for k, v in data["target"].items() if v and not k.startswith("_")
        }
        data["condition"] = str(data["condition"])

        function_name = data.pop("function_name")
        if flowmapper_metadata:
            data["flowmapper_metadata"] = {
                "version": __version__,
                "function_name": function_name,
            }

        return data

    def __lt__(self, other: "Match") -> bool:
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
