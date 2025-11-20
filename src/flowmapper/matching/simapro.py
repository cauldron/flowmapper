from functools import partial

from randonneur_data import Registry

from flowmapper.matching.transformation import match_with_transformation

manual_simapro_ecoinvent_mapping = partial(
    match_with_transformation,
    transformation="simapro-2024-biosphere-ecoinvent-3.10-biosphere",
    fields=["name"],
)
manual_simapro_ecoinvent_mapping.__name__ = (
    "match_with_transformation_simapro_2024_to_ecoinvent_310"
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
    dp["update"] = [row for row in dp["update"] if not row["source"]["context"].endswith("indoor")]

    for row in dp["update"]:
        # Our source flows are already normalized to this form
        row["source"]["context"] = context_mapping[row["source"]["context"]]

    # for row in dp["update"]:
    #     if row["source"]["name"] == "Particulates, > 10 um" and row["source"]["context"][0] == "air":
    #         print(row)

    return dp


simapro_ecoinvent_glad_name_matching = partial(
    match_with_transformation,
    transformation=_get_normalized_matching(),
    fields=["name", "context"],
)
simapro_ecoinvent_glad_name_matching.__name__ = (
    "match_names_using_transitive_simapro_2025_to_ecoinvent_312_through_ef_31"
)
