from dataclasses import dataclass, field
from typing import Self

from flowmapper.cas import CASField
from flowmapper.context import ContextField
from flowmapper.string_field import StringField
from flowmapper.string_list import StringList
from flowmapper.unit import UnitField
from flowmapper.utils import apply_transformations, generate_flow_id


@dataclass
class Flow:
    name: StringField
    unit: UnitField
    content: ContextField
    identifier: StringField | None = None
    location: StringField | None = None
    oxidation_state: OxidationState | None = None
    cas: CASField | None = None
    synonyms: StringList = field(default_factory=lambda: StringList([]))


    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=StringField(data["name"]),
        )


@dataclass
class VersionedFlow:
    original: Flow
    normalized: Flow


class Flow:
    def __init__(
        self,
        data: dict,
        transformations: list[dict] | None = None,
    ):
        # Hash of sorted dict keys and values
        self.id = generate_flow_id(data)
        self.data = data
        self.transformed = apply_transformations(data, transformations)
        self.conversion_factor = self.transformed.get("conversion_factor")
        self.identifier = StringField(
            original=self.data.get("identifier"),
            transformed=self.transformed.get("identifier"),
            use_lowercase=False,
        )
        self.name = StringField(
            original=self.data.get("name"),
            transformed=self.transformed.get("name"),
        )
        self.unit = UnitField(
            original=self.data.get("unit"),
            transformed=self.transformed.get("unit"),
        )
        self.context = ContextField(
            original=self.data.get("context"),
            transformed=self.transformed.get("context"),
        )
        self.cas = CASField(data.get("CAS number"))
        self.synonyms = StringList(
            original=self.data.get("synonyms", []),
            transformed=self.transformed.get("synonyms", []),
        )

    @property
    def uniqueness_id(self):
        tupleize = lambda x: tuple(x) if isinstance(x, list) else x
        return (
            self.name.original,
            tupleize(self.context.original),
            self.unit.original,
            self.identifier.original,
        )

    @property
    def missing(self):
        """This flow has been marked as missing in target list"""
        return self.transformed.get("__missing__")

    @property
    def export(self) -> dict:
        return {
            k: v
            for k, v in [
                ("name", self.name.original),
                ("unit", self.unit.original),
                ("identifier", self.identifier.original),
                ("context", self.context.original),
                ("CAS number", self.cas.export),
            ]
            if v
        }

    def __repr__(self) -> str:
        return f"""Flow object:
    Identifier: {self.identifier}
    Name: {self.name}
    Context: {self.context}
    Unit: {self.unit}"""

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    # Used in sorting
    def __lt__(self, other):
        return self.name.normalized < other.name.normalized
