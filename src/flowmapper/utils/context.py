"""Context-related utility functions."""

from typing import Any

MISSING_VALUES = {
    "",
    "(unknown)",
    "(unspecified)",
    "null",
    "unknown",
    "unspecified",
}


def as_normalized_tuple(value: Any) -> tuple[str]:
    """Convert context inputs to normalized tuple form."""
    if isinstance(value, (tuple, list)):
        intermediate = value
    elif isinstance(value, str) and "/" in value:
        intermediate = list(value.split("/"))
    elif isinstance(value, str):
        intermediate = [value]
    else:
        raise ValueError(f"Can't understand input context {value}")

    intermediate = [elem.lower().strip() for elem in intermediate]

    while intermediate and intermediate[-1] in MISSING_VALUES:
        if len(intermediate) == 1:
            break
        intermediate = intermediate[:-1]

    return tuple(intermediate)


def tupleize_context(obj: dict) -> dict:
    """Convert `context` value to `tuple` if possible.

    Handles both individual migration objects and full datapackage structures.
    For datapackages, iterates through verb keys (like "update", "create") and
    processes all migration objects in those lists.
    """
    # Handle datapackage structure with verb keys (update, create, etc.)
    if isinstance(obj, dict):
        # Check if this looks like a datapackage (has verb keys with lists)
        verb_keys = ["update", "create", "delete", "rename"]
        has_verb_keys = any(
            key in obj and isinstance(obj[key], list) for key in verb_keys
        )

        if has_verb_keys:
            # This is a datapackage - process each verb's list
            for verb in verb_keys:
                if verb in obj and isinstance(obj[verb], list):
                    for migration_obj in obj[verb]:
                        if isinstance(migration_obj, dict):
                            tupleize_context(migration_obj)
            return obj

    # Handle individual migration object or dict with context
    if isinstance(obj, dict):
        # Process top-level context if present
        if "context" in obj and not isinstance(obj["context"], str):
            obj["context"] = as_normalized_tuple(obj["context"])

        # Recursively process source and target
        if isinstance(obj.get("source"), dict):
            tupleize_context(obj["source"])
        if isinstance(obj.get("target"), dict):
            tupleize_context(obj["target"])

    return obj
