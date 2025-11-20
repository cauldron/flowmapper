"""Field classes and utilities for Flow attributes.

This package contains field classes and related utilities used by Flow objects:
- CASField: Chemical Abstracts Service registry number field
- ContextField: Context field for flow categorization
- StringField: String field with normalization support
- OxidationState: Oxidation state representation
- Location utilities: Functions for extracting and manipulating location codes
"""

from flowmapper.fields.cas import CASField
from flowmapper.fields.context import ContextField
from flowmapper.fields.location import replace_location_suffix, split_location_suffix
from flowmapper.fields.oxidation_state import OxidationState
from flowmapper.fields.string_field import StringField

__all__ = [
    "CASField",
    "ContextField",
    "StringField",
    "OxidationState",
    "replace_location_suffix",
    "split_location_suffix",
]
