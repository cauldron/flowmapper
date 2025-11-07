import logging

from flowmapper.constants import RESOURCE_PARENT_CATEGORY
from flowmapper.flow import Flow
from flowmapper.utils import (
    ends_with_location,
    location_reverser,
    names_and_locations,
    rm_parentheses_roman_numerals,
    rm_roman_numerals_ionic_state,
)
from flowmapper.preferred_synonyms import (
    match_identical_names_in_preferred_synonyms,
    match_identical_names_in_synonyms,
)

logger = logging.getLogger(__name__)


def format_match_result(s: Flow, t: Flow, conversion_factor: float, match_info: dict):
    return match_info | {
        "source": s.export,
        "target": t.export,
        "conversion_factor": conversion_factor,
    }


def match_identical_identifier(s: Flow, t: Flow, comment: str = "Identical identifier"):
    if s.identifier and (s.identifier == t.identifier):
        return {"comment": comment}


def match_identical_cas_numbers(
    s: Flow, t: Flow, comment: str = "Identical CAS numbers"
):
    if (s.cas == t.cas) and (s.context == t.context):
        return {"comment": comment}


def match_identical_names(s: Flow, t: Flow, comment="Identical names"):
    if (s.name == t.name) and (s.context == t.context):
        return {"comment": comment}


def match_identical_names_without_commas(
    s: Flow, t: Flow, comment="Identical names when commas removed"
):
    if (s.name.normalized.replace(",", "") == t.name.normalized.replace(",", "")) and (
        s.context == t.context
    ):
        return {"comment": comment}


def match_resources_with_wrong_subcontext(s: Flow, t: Flow):
    if (
        s.context.normalized[0].lower() in RESOURCE_PARENT_CATEGORY
        and t.context.normalized[0].lower() in RESOURCE_PARENT_CATEGORY
        and s.name == t.name
    ):
        return {"comment": "Resources with identical name but wrong subcontext"}


def match_identical_names_except_missing_suffix(
    s: Flow, t: Flow, suffix: str, comment: str = "Identical names except missing suffix"
) -> dict:
    if (
        (f"{s.name.normalized}, {suffix}" == t.name)
        or (f"{t.name.normalized}, {suffix}" == s.name)
        or (f"{s.name.normalized} {suffix}" == t.name)
        or (f"{t.name.normalized} {suffix}" == s.name)
    ) and s.context == t.context:
        return {"comment": comment}


def match_names_with_roman_numerals_in_parentheses(
    s: Flow, t: Flow, comment="With/without roman numerals in parentheses"
):
    if (
        rm_parentheses_roman_numerals(s.name.normalized)
        == rm_parentheses_roman_numerals(t.name.normalized)
        and s.context == t.context
    ):
        return {"comment": comment}


def match_custom_names_with_location_codes(
    s: Flow, t: Flow, comment="Custom names with location code"
):
    """Matching which pulls out location codes but also allows for custom name transformations."""
    match = ends_with_location.search(s.name.normalized)
    if match:
        location = location_reverser[match.group("code")]
        # Don't use replace, it will find e.g. ", fr" in "transformation, from"
        name = s.name.normalized[: -len(match.group())]
        try:
            mapped_name = names_and_locations[name]["target"]
        except KeyError:
            return
        if mapped_name == t.name.normalized and s.context == t.context:
            result = {"comment": comment, "location": location} | names_and_locations[
                name
            ].get("extra", {})
            if (
                s.name.normalized.startswith("water")
                and s.unit.normalized == "cubic_meter"
                and t.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 1000
            elif (
                s.name.normalized.startswith("water")
                and t.unit.normalized == "cubic_meter"
                and s.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 0.001
            return result


def match_names_with_location_codes(
    s: Flow, t: Flow, comment="Name matching with location code"
):
    match = ends_with_location.search(s.name.normalized)
    if match:
        location = location_reverser[match.group("code")]
        name = s.name.normalized.replace(match.group(), "")
        if name == t.name.normalized and s.context == t.context:
            result = {"comment": comment, "location": location}
            if (
                s.name.normalized.startswith("water")
                and s.unit.normalized == "cubic_meter"
                and t.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 1000.0
            elif (
                s.name.normalized.startswith("water")
                and t.unit.normalized == "cubic_meter"
                and s.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 0.001
            return result


def match_resource_names_with_location_codes_and_parent_context(
    s: Flow, t: Flow, comment="Name matching with location code and parent context"
):
    """Sometimes we have flows in a parent context,"""
    match = ends_with_location.search(s.name.normalized)
    if match:
        location = location_reverser[match.group("code")]
        name = s.name.normalized.replace(match.group(), "")
        if (
            name == t.name.normalized
            and s.context.normalized[0].lower() in RESOURCE_PARENT_CATEGORY
            and t.context.normalized[0].lower() in RESOURCE_PARENT_CATEGORY
        ):
            result = {"comment": comment, "location": location}
            if (
                s.name.normalized.startswith("water")
                and s.unit.normalized == "cubic_meter"
                and t.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 1000.0
            elif (
                s.name.normalized.startswith("water")
                and t.unit.normalized == "cubic_meter"
                and s.unit.normalized == "kilogram"
            ):
                result["conversion_factor"] = 0.001
            return result


def match_non_ionic_state(
    s: Flow, t: Flow, comment="Non-ionic state if no better match"
):
    if (
        (rm_roman_numerals_ionic_state(s.name.normalized) == t.name)
        or (rm_roman_numerals_ionic_state(s.name.normalized) + ", ion" == t.name)
    ) and s.context == t.context:
        return {"comment": comment}


def match_biogenic_to_non_fossil(
    s: Flow, t: Flow, comment="Biogenic to non-fossil if no better match"
):
    if (
        s.name.normalized.removesuffix(", biogenic")
        == t.name.normalized.removesuffix(", non-fossil")
        and s.context == t.context
    ):
        return {"comment": comment}


def match_resources_with_suffix_in_ground(s: Flow, t: Flow):
    return match_identical_names_except_missing_suffix(
        s, t, suffix="in ground", comment="Resources with suffix in ground"
    )


def match_flows_with_suffix_unspecified_origin(s: Flow, t: Flow):
    return match_identical_names_except_missing_suffix(
        s,
        t,
        suffix="unspecified origin",
        comment="Flows with suffix unspecified origin",
    )


def match_resources_with_suffix_in_water(s: Flow, t: Flow):
    return match_identical_names_except_missing_suffix(
        s, t, suffix="in water", comment="Resources with suffix in water"
    )


def match_resources_with_suffix_in_air(s: Flow, t: Flow):
    return match_identical_names_except_missing_suffix(
        s, t, suffix="in air", comment="Resources with suffix in air"
    )


def match_emissions_with_suffix_ion(s: Flow, t: Flow):
    return match_identical_names_except_missing_suffix(
        s, t, suffix="ion", comment="Match emissions with suffix ion"
    )


def match_rules():
    return [
        match_identical_identifier,
        match_identical_names,
        match_identical_names_without_commas,
        match_resources_with_suffix_in_ground,
        match_resources_with_suffix_in_water,
        match_resources_with_suffix_in_air,
        match_flows_with_suffix_unspecified_origin,
        match_resources_with_wrong_subcontext,
        match_emissions_with_suffix_ion,
        match_names_with_roman_numerals_in_parentheses,
        match_names_with_location_codes,
        match_resource_names_with_location_codes_and_parent_context,
        match_custom_names_with_location_codes,
        match_identical_cas_numbers,
        match_non_ionic_state,
        match_biogenic_to_non_fossil,
        match_identical_names_in_preferred_synonyms,
        match_identical_names_in_synonyms,
    ]
