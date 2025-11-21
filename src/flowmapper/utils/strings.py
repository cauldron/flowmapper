"""String manipulation utility functions."""

import unicodedata
from collections.abc import Collection, Mapping
from typing import Any


def normalize_str(s: Any) -> str:
    """Normalize a string using Unicode NFC normalization and strip whitespace."""
    if s is not None:
        return unicodedata.normalize("NFC", s).strip()
    else:
        return ""


def rowercase(obj: Any) -> Any:
    """Recursively transform everything to lower case recursively."""
    if isinstance(obj, str):
        return obj.lower()
    elif isinstance(obj, Mapping):
        return type(obj)([(rowercase(k), rowercase(v)) for k, v in obj.items()])
    elif isinstance(obj, Collection):
        return type(obj)([rowercase(o) for o in obj])
    else:
        return obj
