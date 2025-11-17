from __future__ import annotations

import copy
import importlib.resources as resource
import json
import re
import unicodedata
from collections.abc import Callable, Collection, Mapping
from contextlib import AbstractContextManager
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from randonneur import Datapackage, MigrationConfig, migrate_nodes
from randonneur_data import Registry

if TYPE_CHECKING:
    from flowmapper.domain import Flow, NormalizedFlow

logger = structlog.get_logger("flowmapper")
default_registry = Registry()
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
    from flowmapper.domain import Flow

    func = randonneur_as_function(
        datapackage=datapackage, fields=fields, registry=registry
    )
    transformed_data = func(graph=[nf.normalized.to_dict() for nf in flows])

    for flow, data_dict in zip(flows, transformed_data):
        flow.current = Flow.from_dict(data_dict)

    return flows


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
