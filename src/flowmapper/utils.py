from __future__ import annotations

import copy
import importlib.resources as resource
import json
import re
import unicodedata
from collections.abc import Callable, Collection, Mapping
from contextlib import AbstractContextManager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from flowmapper.domain import Flow

logger = structlog.get_logger("flowmapper")

RESULTS_DIR = Path(__file__).parent / "manual_matching" / "results"


with resource.as_file(
    resource.files("flowmapper") / "data" / "names_and_locations.json"
) as filepath:
    names_and_locations = {o["source"]: o for o in json.load(open(filepath))}

try:
    import cytoolz as toolz
except ImportError:
    logger.info("Install `cytoolz` to get a speed up in matching functions")
    import toolz

assert toolz  # Do not delete the import call stupid linter


def tupleize_context(obj: dict) -> dict:
    """Convert `context` value to `tuple` if possible"""
    if "context" not in obj:
        return obj
    elif not isinstance(obj["context"], str):
        obj["context"] = tuple(obj["context"])
    return obj


def load_standard_transformations() -> list:
    # with resource.as_file(
    #     resource.files("flowmapper") / "data" / "standard-units-harmonization.json"
    # ) as filepath:
    #     units = json.load(open(filepath))
    with resource.as_file(
        resource.files("flowmapper") / "data" / "simapro-2023-ecoinvent-3-contexts.json"
    ) as filepath:
        contexts = json.load(open(filepath))
    # return [units, contexts]
    return [contexts]


def read_migration_files(*filepaths: str | Path) -> list[dict]:
    """
    Read and aggregate migration data from multiple JSON files.

    This function opens and reads a series of JSON files, each containing migration data as a list of dicts without the change type.
    It aggregates all changes into a single list and returns it wrapped in a dictionary
    under the change type 'update'.

    Parameters
    ----------
    *filepaths : Path
        Variable length argument list of Path objects.

    Returns
    -------
    dict
        A dictionary containing a single key 'update', which maps to a list. This list is
        an aggregation of the data from all the JSON files read.
    """
    migration_data = []

    for filepath in filepaths:
        if (RESULTS_DIR / filepath).is_file():
            filepath = RESULTS_DIR / filepath
        with open(Path(filepath)) as fs:
            migration_data.append(json.load(fs))

    return migration_data


def normalize_str(s: Any) -> str:
    if s is not None:
        return unicodedata.normalize("NFC", s).strip()
    else:
        return ""


def transform_flow(flow, transformation):
    result = copy.copy(flow)
    result.update(transformation["target"])
    return result


def matcher(source, target):
    return all(target.get(key) == value for key, value in source.items())


def rowercase(obj: Any) -> Any:
    """Recursively transform everything to lower case recursively"""
    if isinstance(obj, str):
        return obj.lower()
    elif isinstance(obj, Mapping):
        return type(obj)([(rowercase(k), rowercase(v)) for k, v in obj.items()])
    elif isinstance(obj, Collection):
        return type(obj)([rowercase(o) for o in obj])
    else:
        return obj


def apply_transformations(obj: dict, transformations: list[dict] | None) -> dict:
    if not transformations:
        return obj
    obj = copy.deepcopy(obj)
    lower = rowercase(obj)

    for dataset in transformations:
        for transformation_obj in dataset.get("create", []):
            if matcher(
                transformation_obj,
                lower if dataset.get("case-insensitive") else obj,
            ):
                # Marked an needs to be created; missing in target list
                obj["__missing__"] = True
                break
        for transformation_obj in dataset.get("update", []):
            source_to_match = lower if dataset.get("case-insensitive") else obj
            if dataset.get("case-insensitive"):
                source_transformation = (
                    rowercase(transformation_obj["source"])
                    if isinstance(transformation_obj["source"], dict)
                    else transformation_obj["source"]
                )
            else:
                source_transformation = transformation_obj["source"]
            if matcher(source_transformation, source_to_match):
                obj.update(transformation_obj["target"])
                if "conversion_factor" in transformation_obj:
                    obj["conversion_factor"] = transformation_obj["conversion_factor"]
                break

    return obj


unit_slash = re.compile(r"/(?P<unit>m3|kg)(\,?\s+|\s+|$)")


def remove_unit_slash(obj: Flow) -> str:
    name = obj.name.data
    if match := unit_slash.search(name):
        obj_dict = match.groupdict()
        if match.end() == len(name):
            name = name[: match.start()]
        else:
            name = name[: match.start()] + ", " + name[match.end() :]
        if not obj.unit.compatible(obj_dict["unit"]):
            logger.warning(
                f"Flow {obj} has unit '{obj.unit}' but name refers to incompatible unit '{obj_dict['unit']}'"
            )
    return name


class FlowTransformationContext(AbstractContextManager):
    """
    Context manager that applies a function to NormalizedFlows on entry and resets them on exit.

    This context manager is useful when you need to temporarily modify flows for matching
    or processing, and want to ensure they are reset to their normalized state afterward.

    Parameters
    ----------
    flows : list[NormalizedFlow]
        List of NormalizedFlow objects to transform and reset.
    functions : list[Callable[[list[NormalizedFlow]], None]]
        Function to apply to the flows on context entry. The function should modify
        the normalized flows in place (e.g., by calling update_current on them).

    Examples
    --------
    >>> flows = [NormalizedFlow(...), NormalizedFlow(...)]
    >>> def update_func_a(flows):
    ...     for flow in flows:
    ...         flow.update_current(name="Modified")
    >>> def update_func_b(flows):
    ...     for flow in flows:
    ...         flow.update_current(unit="A lot")
    >>> with FlowTransformationContext(flows, update_func_a, update_func_b):
    ...     # flows are modified here
    ...     pass
    >>> # flows are automatically reset to normalized state
    """

    def __init__(
        self,
        flows: list[Any],  # list[NormalizedFlow] but avoiding circular import
        *functions: Callable[[list[Any]], None],
    ):
        self.flows = flows
        self.functions = functions

    def __enter__(self) -> FlowTransformationContext:
        """Apply the function to the flows on entry."""
        for function in self.functions:
            function(self.flows)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Reset all flows to their normalized state on exit."""
        for flow in self.flows:
            flow.reset_current()
