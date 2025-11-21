from functools import partial

from randonneur_data import Registry

from flowmapper.domain.match_condition import MatchCondition
from flowmapper.matching import match_identical_names_lowercase
from flowmapper.matching.context import match_resources_with_wrong_subcontext
from flowmapper.matching.core import transform_and_then_match
from flowmapper.matching.specialized import add_missing_regionalized_flows
from flowmapper.utils import apply_randonneur

manual_simapro_ecoinvent_mapping = partial(
    transform_and_then_match,
    match_function=partial(
        match_identical_names_lowercase,
        function_name="manual_simapro_ecoinvent_mapping",
        comment="Shared normalized attributes after applying transformation: simapro-2024-biosphere-ecoinvent-3.10-biosphere",
        match_condition=MatchCondition.related,
    ),
    transform_source_flows=[
        partial(
            apply_randonneur,
            datapackage="simapro-2024-biosphere-ecoinvent-3.10-biosphere",
            fields=["name", "unit"],
        )
    ],
)
manual_simapro_ecoinvent_mapping.__name__ = "manual_simapro_ecoinvent_mapping"


manual_simapro_ecoinvent_mapping_add_regionalized_flows = partial(
    transform_and_then_match,
    match_function=partial(
        add_missing_regionalized_flows,
        function_name="manual_simapro_ecoinvent_mapping_add_regionalized_flows",
    ),
    transform_source_flows=[
        partial(
            apply_randonneur,
            datapackage="simapro-2024-biosphere-ecoinvent-3.10-biosphere",
            fields=["name", "unit"],
        )
    ],
)
manual_simapro_ecoinvent_mapping_add_regionalized_flows.__name__ = (
    "manual_simapro_ecoinvent_mapping_add_regionalized_flows"
)


manual_simapro_ecoinvent_mapping_resource_wrong_subcontext = partial(
    transform_and_then_match,
    match_function=partial(
        match_resources_with_wrong_subcontext,
        function_name="manual_simapro_ecoinvent_mapping_resource_wrong_subcontext",
    ),
    transform_source_flows=[
        partial(
            apply_randonneur,
            datapackage="simapro-2024-biosphere-ecoinvent-3.10-biosphere",
            fields=["name", "unit"],
        )
    ],
)
manual_simapro_ecoinvent_mapping_resource_wrong_subcontext.__name__ = (
    "manual_simapro_ecoinvent_mapping_resource_wrong_subcontext"
)


def _get_normalized_matching() -> dict:
    registry = Registry()

    context_mapping = {
        line["source"]["context"]: line["target"]["context"]
        for line in registry.get_file("SimaPro-2025-ecoinvent-3.12-context")["update"]
    }

    dp = registry.get_file(
        "simapro-2025-biosphere-ef-3.1-biosphere-ecoinvent-3.12-biosphere-transitive"
    )

    # for row in dp["update"]:
    #     if row["source"]["name"] == "Particulates, > 10 um" and row["source"]["context"].startswith("Air"):
    #         print(row)

    # print()

    # Remove indoor mappings - these were deleted from ecoinvent, so map to other subcontexts.
    # However, there is no guarantee that they will have the _same_ mapping in that subcontext
    # as the other, existing mapping, and multiple conflicting mappings will raise an error.
    dp["update"] = [
        row for row in dp["update"] if not row["source"]["context"].endswith("indoor")
    ]

    for row in dp["update"]:
        # Our source flows are already normalized to this form
        row["source"]["context"] = context_mapping[row["source"]["context"]]

    # for row in dp["update"]:
    #     if row["source"]["name"] == "Particulates, > 10 um" and row["source"]["context"][0] == "air":
    #         print(row)

    return dp


simapro_ecoinvent_glad_name_matching = partial(
    transform_and_then_match,
    transform_source_flows=[
        partial(
            apply_randonneur,
            datapackage=_get_normalized_matching(),
            fields=["name", "context"],
        )
    ],
    match_function=partial(
        match_identical_names_lowercase,
        function_name="simapro_ecoinvent_glad_name_matching",
        comment="Shared normalized attributes after applying transformation: simapro-2025-biosphere-ef-3.1-biosphere-ecoinvent-3.12-biosphere-transitive",
        match_condition=MatchCondition.related,
    ),
)
simapro_ecoinvent_glad_name_matching.__name__ = "simapro_ecoinvent_glad_name_matching"
