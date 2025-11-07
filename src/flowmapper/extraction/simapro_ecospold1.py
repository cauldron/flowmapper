import json
from pathlib import Path

import pyecospold
from loguru import logger

# def is_simapro_csv_file(fp: Path) -> bool:
#     if not fp.is_file() or not fp.suffix.lower() == ".csv":
#         return False
#     try:
#         bw_simapro_csv.header.parse_header(open(fp, encoding="sloppy-windows-1252"))[0].project
#         return True
#     except:
#         logger.critical("Skipping {a} as we can't read it as a SimaPro file", a=fp.name)
#         return False


def simapro_ecospold1_biosphere_extractor(dirpath: Path, output_fp: Path) -> None:
    """Load all simapro files in directory `dirpath`, and extract all biosphere flows"""
    flows = set()

    for _, es in pyecospold.parse_directory_v1(dirpath):
        for ds in es.datasets:
            for exc in ds.flowData:
                if exc.groupsStr[0] in ("ToNature", "FromNature"):
                    flows.add(((exc.category, exc.subCategory), exc.name, exc.unit))

    with open(output_fp, "w") as f:
        json.dump(
            [{"context": c, "name": n, "unit": u} for c, n, u in sorted(flows)],
            f,
            indent=2,
            ensure_ascii=False,
        )
