import json
import logging
from collections.abc import Callable
from pathlib import Path

from randonneur import Datapackage
from randonneur_data import Registry

from flowmapper.domain.flow import Flow
from flowmapper.domain.match import Match
from flowmapper.flowmap import Flowmap
from flowmapper.utils import (
    apply_transformation_and_convert_flows_to_normalized_flows,
    randonneur_as_function,
)

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
    transformations: list[Datapackage | str | dict | Callable] | None = None,
    rules: list[Callable[..., list[Match]]] | None = None,
    unit_normalization: bool = True,
    licenses: list | None = None,
    homepage: str | None = None,
    name: str | None = None,
    registry: Registry | None = None,
    no_matching: bool = False,
) -> Flowmap:
    """
    Generate mappings between elementary flows lists
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    transformation_functions = []

    if transformations is None:
        transformations = []

    if unit_normalization:
        transformations.append("Flowmapper-standard-units-harmonization")

    for obj in transformations:
        if isinstance(obj, (str, dict, Datapackage)):
            transformation_functions.append(
                randonneur_as_function(datapackage=obj, registry=registry)
            )
        elif isinstance(obj, Callable):
            transformation_functions.append(obj)
        else:
            raise ValueError(f"Can't understand transformation {obj}")

    original_source_flows = [Flow.from_dict(obj) for obj in json.load(open(source))]
    source_flows = apply_transformation_and_convert_flows_to_normalized_flows(
        functions=transformation_functions, flows=original_source_flows
    )

    original_target_flows = [Flow.from_dict(obj) for obj in json.load(open(target))]
    target_flows = apply_transformation_and_convert_flows_to_normalized_flows(
        functions=transformation_functions, flows=original_target_flows
    )

    flowmap = Flowmap(
        source_flows=source_flows,
        target_flows=target_flows,
        data_preparation_functions=transformation_functions,
        rules=rules,
    )
    if no_matching:
        return flowmap
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
