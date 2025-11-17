import itertools
import logging
from collections.abc import Callable
from functools import partial

from rapidfuzz.distance.DamerauLevenshtein import distance

from flowmapper.domain import Flow, Match, MatchCondition, NormalizedFlow
from flowmapper.utils import FlowTransformationContext, apply_randonneur, toolz

logger = logging.getLogger(__name__)

# Note: It might seem like running these functions in parallel would be much faster, but in
# practice it doesn't seem to be. The memory overhead of copying over very large sets of target
# flows means parallel execution was twice as slow, at least in my testing.


def get_matches(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
    comment: str,
    function_name: str,
    match_condition: MatchCondition,
    conversion_factors: list[float] | None = None,
) -> list[Match]:
    if not target_flows:
        return []

    matches = []

    # Providing conversion_factors only makes sense if there is a single target flow
    # Otherwise you have M-to-N problem
    if conversion_factors is None:
        cfs = itertools.repeat(None)
    else:
        if not len(conversion_factors) == len(source_flows):
            raise ValueError(
                f"`conversion_factors` (length {len(conversion_factors)}) must have same length as `source_flows` (length {len(source_flows)})"
            )
        cfs = conversion_factors

    for conversion_factor, source in zip(cfs, source_flows):
        targets = [flow for flow in target_flows if flow.unit_compatible(flow)]
        if len(targets) > 1:
            # Try find most-appropriate match if more than one is present. Added because ecoinvent
            # deprecated most stratospheric emissions and redirected them to air, unspecified, so
            # now all air, unspecified emissions have multiple targets.
            targets = [
                target
                for target in targets
                if target.normalized.context == source.normalized.context
            ]
        if len(targets) == 1:
            target = target_flows[0]
            source.matched = True
            if conversion_factor is None:
                conversion_factor = source.conversion_factor(target)
            matches.append(
                Match(
                    source=source.original,
                    target=target.original,
                    function_name=function_name,
                    comment=comment or "",
                    condition=match_condition,
                    conversion_factor=conversion_factor,
                )
            )

    return matches


def match_identical_identifier(
    source_flows: list[NormalizedFlow],
    target_flows: list[NormalizedFlow],
) -> list[Match]:
    matches = []

    for source_id, sources in toolz.itertoolz.groupby(
        lambda x: x.identifier, source_flows
    ).items():
        if not source_id:
            continue
        matches.extend(
            get_matches(
                source_flows=sources,
                # Filter target flows with matching identifier. We don't need to worry about
                # duplicate identifiers as `get_matches` will only allow a single result target
                target_flows=[
                    flow for flow in target_flows if source_id == flow.identifier
                ],
                comment=f"Shared target-unique identifier: {source_id}",
                function_name="match_identical_identifier",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_identical_cas_numbers(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (cas_number, context, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.cas_number, x.context, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.cas_number == cas_number
                    and flow.context == context
                    and flow.location == location
                ],
                comment=f"Shared CAS code with identical context and location: {cas_number}",
                function_name="match_identical_cas_numbers",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_identical_names(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    target
                    for target in target_flows
                    if target.name == name
                    and target.context == context
                    and target.oxidation_state == oxidation_state
                    and target.location == location
                ],
                comment=f"Shared normalized name with identical context, oxidation state, and location: {name}",
                function_name="match_identical_names",
                match_condition=MatchCondition.exact,
            )
        )

    return matches


def match_close_names(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    target
                    for target in target_flows
                    if distance(
                        str(target.name), str(name), processor=lambda x: x.lower()
                    )
                    < 3
                    and target.context == context
                    and target.oxidation_state == oxidation_state
                    and target.location == location
                ],
                comment=f"Name has Damerau Levenshtein edit distance of 2 or lower with identical context, oxidation state, and location: {name}",
                function_name="match_close_names",
                match_condition=MatchCondition.related,
            )
        )

    return matches


def match_ecoinvent_transitive_matching(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    func: Callable[[list[NormalizedFlow]], list[NormalizedFlow]] = partial(
        apply_randonneur,
        datapackage="ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive",
        fields=["name", "context"],
    )

    with (
        FlowTransformationContext(source_flows, func) as sf,
        FlowTransformationContext(target_flows, func) as tf,
    ):
        for (name, context, location), sources in toolz.itertoolz.groupby(
            lambda x: (x.name, x.context, x.location), sf
        ).items():
            matches.extend(
                get_matches(
                    source_flows=sources,
                    target_flows=[
                        target
                        for target in tf
                        if target.name.lower() == name.lower()
                        and target.context == context
                        and target.location == location
                    ],
                    comment=f"Shared normalized name when transitively harmonized to ecoinvent 3.12 with identical context and location: {name}",
                    function_name="match_ecoinvent_transitive_matching",
                    match_condition=MatchCondition.close,
                )
            )

    return matches


def match_with_transformation(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow], transformation: str, fields: list[str]
) -> list[Match]:
    matches = []

    func: Callable[[list[NormalizedFlow]], list[NormalizedFlow]] = partial(
        apply_randonneur,
        datapackage=transformation,
        fields=fields,
    )

    with FlowTransformationContext(source_flows, func) as sf:
        for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
            lambda x: (x.name, x.context, x.oxidation_state, x.location), sf
        ).items():
            matches.extend(
                get_matches(
                    source_flows=sources,
                    target_flows=[
                        target
                        for target in target_flows
                        if target.name == name
                        and target.context == context
                        and target.oxidation_state == oxidation_state
                        and target.location == location
                    ],
                    comment=f"Shared normalized attributes after applying transformation: {transformation}",
                    function_name="match_with_transformation",
                    match_condition=MatchCondition.related,
                )
            )

    return matches


def match_identical_names_lowercase(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        name = name.lower()
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name.lower() == name
                    and flow.context == context
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized lowercase name with identical context, oxidation state, and location: {name}",
                function_name="match_identical_names_lowercase",
                match_condition=MatchCondition.close,
            )
        )

    return matches


def match_identical_names_without_commas(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, context, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.context, x.oxidation_state, x.location), source_flows
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name.replace(",", "") == name.replace(",", "")
                    and flow.context == context
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized name with commas removed and identical context, oxidation state, and location: {name}",
                match_condition=MatchCondition.close,
                function_name="match_identical_names_without_commas",
            )
        )

    return matches


def match_resources_with_wrong_subcontext(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, oxidation_state, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.oxidation_state, x.location),
        filter(lambda f: f.normalized.context.is_resource(), source_flows),
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name == name
                    and flow.normalized.context.is_resource()
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment=f"Shared normalized name and resource-type context, with identical oxidation state and location: {name}",
                match_condition=MatchCondition.close,
                function_name="match_resources_with_wrong_subcontext",
            )
        )

    return matches


def match_identical_names_except_missing_suffix(
    source_flows: list[Flow],
    target_flows: list[Flow],
    suffix: str,
    comment: str = "Identical names except missing suffix",
) -> dict:
    if (
        (f"{s.name.normalized}, {suffix}" == t.name)
        or (f"{t.name.normalized}, {suffix}" == s.name)
        or (f"{s.name.normalized} {suffix}" == t.name)
        or (f"{t.name.normalized} {suffix}" == s.name)
    ) and s.context == t.context:
        return {"comment": comment}


# def match_names_with_roman_numerals_in_parentheses(
#     source_flows: list[Flow], target_flows: list[Flow], comment="With/without roman numerals in parentheses"
# ):
#     if (
#         rm_parentheses_roman_numerals(s.name.normalized)
#         == rm_parentheses_roman_numerals(t.name.normalized)
#         and s.context == t.context
#     ):
#         return {"comment": comment}


# def match_custom_names_with_location_codes(
#     source_flows: list[Flow], target_flows: list[Flow], comment="Custom names with location code"
# ):
#     """Matching which pulls out location codes but also allows for custom name transformations."""
#     match = ends_with_location.search(s.name.normalized)
#     if match:
#         location = location_reverser[match.group("code")]
#         # Don't use replace, it will find e.g. ", fr" in "transformation, from"
#         name = s.name.normalized[: -len(match.group())]
#         try:
#             mapped_name = names_and_locations[name]["target"]
#         except KeyError:
#             return
#         if mapped_name == t.name.normalized and s.context == t.context:
#             result = {"comment": comment, "location": location} | names_and_locations[
#                 name
#             ].get("extra", {})
#             if (
#                 s.name.normalized.startswith("water")
#                 and s.unit.normalized == "cubic_meter"
#                 and t.unit.normalized == "kilogram"
#             ):
#                 result["conversion_factor"] = 1000
#             elif (
#                 s.name.normalized.startswith("water")
#                 and t.unit.normalized == "cubic_meter"
#                 and s.unit.normalized == "kilogram"
#             ):
#                 result["conversion_factor"] = 0.001
#             return result


# def match_names_with_location_codes(
#     source_flows: list[Flow], target_flows: list[Flow], comment="Name matching with location code"
# ):
#     match = ends_with_location.search(s.name.normalized)
#     if match:
#         location = location_reverser[match.group("code")]
#         name = s.name.normalized.replace(match.group(), "")
#         if name == t.name.normalized and s.context == t.context:
#             result = {"comment": comment, "location": location}
#             if (
#                 s.name.normalized.startswith("water")
#                 and s.unit.normalized == "cubic_meter"
#                 and t.unit.normalized == "kilogram"
#             ):
#                 result["conversion_factor"] = 1000.0
#             elif (
#                 s.name.normalized.startswith("water")
#                 and t.unit.normalized == "cubic_meter"
#                 and s.unit.normalized == "kilogram"
#             ):
#                 result["conversion_factor"] = 0.001
#             return result


def match_name_and_parent_context(
    source_flows: list[NormalizedFlow], target_flows: list[NormalizedFlow]
) -> list[Match]:
    matches = []

    for (name, oxidation_state, context, location), sources in toolz.itertoolz.groupby(
        lambda x: (x.name, x.oxidation_state, x.context, x.location),
        filter(lambda f: len(f.context) > 1, source_flows),
    ).items():
        matches.extend(
            get_matches(
                source_flows=sources,
                target_flows=[
                    flow
                    for flow in target_flows
                    if flow.name == name
                    and flow.context == context[:-1]
                    and flow.oxidation_state == oxidation_state
                    and flow.location == location
                ],
                comment="Shared normalized name and parent context, with identical oxidation state and location",
                match_condition=MatchCondition.related,
                function_name="match_name_and_parent_context",
            )
        )

    return matches


# def match_non_ionic_state(
#     source_flows: list[Flow], target_flows: list[Flow], comment="Non-ionic state if no better match"
# ):
#     if (
#         (rm_roman_numerals_ionic_state(s.name.normalized) == t.name)
#         or (rm_roman_numerals_ionic_state(s.name.normalized) + ", ion" == t.name)
#     ) and s.context == t.context:
#         return {"comment": comment}


def match_biogenic_to_non_fossil(
    source_flows: list[Flow],
    target_flows: list[Flow],
    comment="Biogenic to non-fossil if no better match",
):
    if (
        s.name.normalized.removesuffix(", biogenic")
        == t.name.normalized.removesuffix(", non-fossil")
        and s.context == t.context
    ):
        return {"comment": comment}


def match_resources_with_suffix_in_ground(
    source_flows: list[Flow], target_flows: list[Flow]
):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        all_source_flows,
        all_target_flows,
        suffix="in ground",
        comment="Resources with suffix in ground",
    )


def match_flows_with_suffix_unspecified_origin(
    source_flows: list[Flow], target_flows: list[Flow]
):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        all_source_flows,
        all_target_flows,
        suffix="unspecified origin",
        comment="Flows with suffix unspecified origin",
    )


def match_resources_with_suffix_in_water(
    source_flows: list[Flow], target_flows: list[Flow]
):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        all_source_flows,
        all_target_flows,
        suffix="in water",
        comment="Resources with suffix in water",
    )


def match_resources_with_suffix_in_air(
    source_flows: list[Flow], target_flows: list[Flow]
):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        all_source_flows,
        all_target_flows,
        suffix="in air",
        comment="Resources with suffix in air",
    )


def match_emissions_with_suffix_ion(source_flows: list[Flow], target_flows: list[Flow]):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        all_source_flows,
        all_target_flows,
        suffix="ion",
        comment="Match emissions with suffix ion",
    )


def match_rules():
    simple_ecoinvent = partial(
        match_with_transformation,
        transformation="ecoinvent-3.10-biosphere-simapro-2024-biosphere",
        fields=["name"],
    )
    simple_ecoinvent.__name__ = "match_with_transformation"

    return [
        match_identical_identifier,
        match_identical_names,
        # match_identical_names_lowercase,
        match_identical_names_without_commas,
        match_ecoinvent_transitive_matching,
        # match_resources_with_suffix_in_ground,
        # match_resources_with_suffix_in_water,
        # match_resources_with_suffix_in_air,
        # match_flows_with_suffix_unspecified_origin,
        match_resources_with_wrong_subcontext,
        match_name_and_parent_context,
        match_close_names,
        simple_ecoinvent,
        # match_emissions_with_suffix_ion,
        # match_names_with_roman_numerals_in_parentheses,
        # match_names_with_location_codes,
        # match_resource_names_with_location_codes_and_parent_context,
        # match_custom_names_with_location_codes,
        match_identical_cas_numbers,
        # match_non_ionic_state,
        # match_biogenic_to_non_fossil,
        # match_identical_names_in_preferred_synonyms,
        # match_identical_names_in_synonyms,
    ]
