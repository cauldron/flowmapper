import json
from pathlib import Path

import pyecospold


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
