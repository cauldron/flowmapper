import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from flowmapper.flow import Flow
from flowmapper.flowmap import Flowmap
from flowmapper.transformation_mapping import prepare_transformations
from flowmapper.utils import load_standard_transformations, read_migration_files

logger = logging.getLogger(__name__)


def sorting_function(obj: dict) -> tuple:
    return (
        obj.get("name", "ZZZ"),
        str(obj.get("context", "ZZZ")),
        obj.get("unit", "ZZZ"),
    )


class OutputFormat(str, Enum):
    all = "all"
    glad = "glad"
    randonneur = "randonneur"


def flowmapper(
    source: Path,
    target: Path,
    mapping_source: dict,
    mapping_target: dict,
    source_id: str,
    target_id: str,
    contributors: list,
    output_dir: Path,
    format: OutputFormat,
    version: str = "1.0.0",
    default_transformations: bool = True,
    transformations: Optional[list[Path | str]] = None,
    unmatched_source: bool = True,
    unmatched_target: bool = True,
    matched_source: bool = False,
    matched_target: bool = False,
    licenses: Optional[list] = None,
    homepage: Optional[str] = None,
    name: Optional[str] = None,
) -> Flowmap:
    """
    Generate mappings between elementary flows lists
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded_transformations = []
    if default_transformations:
        loaded_transformations.extend(load_standard_transformations())
    if transformations:
        loaded_transformations.extend(read_migration_files(*transformations))

    prepared_transformations = prepare_transformations(loaded_transformations)

    source_flows = [
        Flow(flow, prepared_transformations) for flow in json.load(open(source))
    ]
    source_flows = [flow for flow in source_flows if not flow.missing]
    target_flows = [
        Flow(flow, prepared_transformations) for flow in json.load(open(target))
    ]

    flowmap = Flowmap(source_flows, target_flows)
    flowmap.statistics()

    stem = f"{source.stem}-{target.stem}"

    if matched_source:
        with open(output_dir / f"{stem}-matched-source.json", "w") as fs:
            json.dump(
                sorted(
                    [flow.export for flow in flowmap.matched_source],
                    key=sorting_function,
                ),
                fs,
                indent=True,
            )

    if unmatched_source:
        with open(output_dir / f"{stem}-unmatched-source.json", "w") as fs:
            json.dump(
                sorted(
                    [flow.export for flow in flowmap.unmatched_source],
                    key=sorting_function,
                ),
                fs,
                indent=True,
            )

    if matched_target:
        with open(output_dir / f"{stem}-matched-target.json", "w") as fs:
            json.dump(
                sorted(
                    [flow.export for flow in flowmap.matched_target],
                    key=sorting_function,
                ),
                fs,
                indent=True,
            )

    if unmatched_target:
        with open(output_dir / f"{stem}-unmatched-target.json", "w") as fs:
            json.dump(
                sorted(
                    [flow.export for flow in flowmap.unmatched_target],
                    key=sorting_function,
                ),
                fs,
                indent=True,
            )

    if format.value == "randonneur":
        flowmap.to_randonneur(
            source_id=source_id,
            target_id=target_id,
            contributors=contributors,
            mapping_source=mapping_source,
            mapping_target=mapping_target,
            version=version,
            licenses=licenses,
            homepage=homepage,
            name=name,
            path=output_dir / f"{stem}.json",
        )
    elif format.value == "glad":
        flowmap.to_glad(output_dir / f"{stem}.xlsx", missing_source=True)
    else:
        flowmap.to_randonneur(
            source_id=source_id,
            target_id=target_id,
            contributors=contributors,
            mapping_source=mapping_source,
            mapping_target=mapping_target,
            version=version,
            licenses=licenses,
            homepage=homepage,
            name=name,
            path=output_dir / f"{stem}.json",
        )
        flowmap.to_glad(output_dir / f"{stem}.xlsx", missing_source=True)

    return flowmap
