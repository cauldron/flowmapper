import json
from pathlib import Path

import bw_simapro_csv
from loguru import logger


def is_simapro_csv_file(fp: Path) -> bool:
    if not fp.is_file() or not fp.suffix.lower() == ".csv":
        return False
    try:
        bw_simapro_csv.header.parse_header(open(fp, encoding="sloppy-windows-1252"))[
            0
        ].project
        return True
    except:
        logger.critical("Skipping {a} as we can't read it as a SimaPro file", a=fp.name)
        return False


def simapro_csv_biosphere_extractor(input_path: Path, output_path: Path) -> None:
    """Load all simapro files in directory `dirpath`, and extract all biosphere flows"""
    if input_path.is_dir():
        simapro_files = [
            fp for fp in sorted(input_path.iterdir()) if is_simapro_csv_file(fp)
        ]
    elif input_path.is_file():
        simapro_files = [input_path]
    else:
        raise ValueError

    flows = set()

    for fp in simapro_files:
        sp = bw_simapro_csv.SimaProCSV(
            fp, stderr_logs=False, write_logs=False, copy_logs=False
        )
        for process in filter(
            lambda x: isinstance(x, bw_simapro_csv.blocks.Process),
            sp.blocks,
        ):
            for block in filter(
                lambda x: isinstance(
                    x, bw_simapro_csv.blocks.GenericUncertainBiosphere
                ),
                process.blocks.values(),
            ):
                for line in block.parsed:
                    flows.add((line["context"], line["name"], line["unit"]))

    with open(output_path, "w") as f:
        json.dump(
            [{"context": c, "name": n, "unit": u} for c, n, u in sorted(flows)],
            f,
            indent=2,
            ensure_ascii=False,
        )
