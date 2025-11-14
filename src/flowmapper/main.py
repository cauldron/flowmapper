import json
import logging
from copy import copy
from functools import partial
from pathlib import Path

from randonneur import Datapackage, MigrationConfig, migrate_nodes
from randonneur_data import Registry

from flowmapper.domain import Flow, NormalizedFlow
from flowmapper.flowmap import Flowmap
from flowmapper.utils import tupleize_context

logger = logging.getLogger(__name__)


def sorting_function(obj: dict) -> tuple:
    return (
        obj.get("name", "ZZZ"),
        str(obj.get("context", "ZZZ")),
        obj.get("unit", "ZZZ"),
    )


def flowmapper(
    source: Path,
    target: Path,
    source_id: str,
    target_id: str,
    contributors: list,
    output_dir: Path,
    version: str = "1.0.0",
    transformations: list[Datapackage | str] | None = None,
    unit_normalization: bool = True,
    licenses: list | None = None,
    homepage: str | None = None,
    name: str | None = None,
    registry: Registry | None = None,
) -> Flowmap:
    """
    Generate mappings between elementary flows lists
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    transformation_functions = []

    if transformations is None:
        transformations = []
    if registry is None:
        registry = Registry()

    if unit_normalization:
        transformations.append("Flowmapper-standard-units-harmonization")

    for obj in transformations:
        if isinstance(obj, Datapackage):
            obj = obj.data
        elif isinstance(obj, str):
            obj = registry.get_file(obj)
        elif "update" not in obj:
            raise KeyError
        transformation_functions.append(
            partial(
                migrate_nodes,
                migrations=tupleize_context(obj),
                config=MigrationConfig(
                    verbs=["update"],
                    case_sensitive=not obj.get("case-insensitive"),
                ),
            )
        )

    original_source_flows = [Flow.from_dict(obj) for obj in json.load(open(source))]
    processed_source_flows = [obj.to_dict() for obj in original_source_flows]
    original_target_flows = [Flow.from_dict(obj) for obj in json.load(open(target))]
    processed_target_flows = [obj.to_dict() for obj in original_target_flows]

    for function in transformation_functions:
        processed_source_flows = function(graph=processed_source_flows)
    for function in transformation_functions:
        processed_target_flows = function(graph=processed_target_flows)

    normalized_source_flows = [
        Flow.from_dict(obj).normalize() for obj in processed_source_flows
    ]
    normalized_target_flows = [
        Flow.from_dict(obj).normalize() for obj in processed_target_flows
    ]

    source_flows = [
        NormalizedFlow(original=o, normalized=n, current=copy(n))
        for o, n in zip(original_source_flows, normalized_source_flows)
    ]
    target_flows = [
        NormalizedFlow(original=o, normalized=n, current=copy(n))
        for o, n in zip(original_target_flows, normalized_target_flows)
    ]

    flowmap = Flowmap(source_flows, target_flows)
    flowmap.generate_matches()
    flowmap.print_statistics()

    stem = f"{source.stem}-{target.stem}"

    with open(output_dir / f"{stem}-unmatched-source.json", "w") as fs:
        json.dump(
            sorted(
                [flow.export() for flow in source_flows if not flow.matched],
                key=sorting_function,
            ),
            fs,
            indent=True,
        )

    flowmap.to_randonneur(
        source_id=source_id,
        target_id=target_id,
        contributors=contributors,
        mapping_source=Flow.randonneur_mapping(),
        mapping_target=Flow.randonneur_mapping(),
        version=version,
        licenses=licenses,
        homepage=homepage,
        name=name,
        path=output_dir / f"{stem}.json",
    )
    flowmap.to_glad(output_dir / f"{stem}.xlsx", missing_source=True)

    return flowmap
