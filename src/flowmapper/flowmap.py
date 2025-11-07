import math
import warnings
from collections import Counter
from functools import cached_property
from numbers import Number
from pathlib import Path
from collections.abc import Callable

import pandas as pd
import pint
import randonneur
from tqdm import tqdm

from flowmapper import __version__
from flowmapper.errors import DifferingConversions, DifferingMatches
from flowmapper.flow import Flow
from flowmapper.match import format_match_result, match_rules
from flowmapper.utils import match_sort_order


def source_flow_id(obj: Flow, ensure_id: bool = False) -> str:
    return (
        str(obj.identifier.original or "")
        if (obj.identifier.original or not ensure_id)
        else str(obj.id or "")
    )


class Flowmap:
    """
    Crosswalk of flows from a source flow list to a target flow list.

    This class provides functionalities to map flows between different flow lists using a series of predefined match rules.

    Attributes
    ----------
    source_flows : list[Flow]
        The list of (unique) source flows to be mapped.
    source_flows_nomatch : list[Flow]
        The list of (unique) source flows that do not match any rule.
    target_flows : list[Flow]
        The list of target flows for mapping.
    target_flows_nomatch : list[Flow]
        The list of target flows that do not match any rule.

    """

    def __init__(
        self,
        source_flows: list[Flow],
        target_flows: list[Flow],
        rules: list[Callable[..., bool]] = None,
        nomatch_rules: list[Callable[..., bool]] = None,
        disable_progress: bool = False,
    ):
        """
        Initializes the Flowmap with source and target flows, along with optional matching rules.

        Duplicated flows are removed from both source and targets lists.

        Parameters
        ----------
        source_flows : list[Flow]
            The list of source flows to be mapped.
        target_flows : list[Flow]
            The list of target flows for mapping.
        rules : list[Callable[..., bool]], optional
            Custom rules for matching source flows to target flows. Default is the set of rules defined in `match_rules`.
        nomatch_rules : list[Callable[..., bool]], optional
            Rules to identify flows that should not be matched.
        disable_progress : bool, optional
            If True, progress bar display during the mapping process is disabled.

        """
        self.disable_progress = disable_progress
        self.rules = rules if rules else match_rules()
        if nomatch_rules:
            self.source_flows = []
            self.source_flows_nomatch = []

            for flow in source_flows:
                matched = False
                for rule in nomatch_rules:
                    if rule(flow):
                        self.source_flows_nomatch.append(flow)
                        matched = True
                        break
                if not matched:
                    self.source_flows.append(flow)
            self.source_flows = list(dict.fromkeys(self.source_flows))
            self.source_flows_nomatch = list(dict.fromkeys(self.source_flows_nomatch))

            self.target_flows = []
            self.target_flows_nomatch = []

            for flow in target_flows:
                matched = False
                for rule in nomatch_rules:
                    if rule(flow):
                        self.target_flows_nomatch.append(flow)
                        matched = True
                        break
                if not matched:
                    self.target_flows.append(flow)
            self.target_flows = list(dict.fromkeys(self.target_flows))
            self.target_flows_nomatch = list(dict.fromkeys(self.target_flows_nomatch))
        else:
            self.source_flows = list(dict.fromkeys(source_flows))
            self.source_flows_nomatch = []
            self.target_flows = list(dict.fromkeys(target_flows))
            self.target_flows_nomatch = []

    def get_single_match(
        self, source: Flow, source_flows: list[Flow], target_flows: list[Flow], rules: list[Callable]
    ) -> dict | None:
        """
        Try to find a single match for `source` in `target_flows` using `rules`.

        Adds to `all_mappings` if found.
        """

        def get_conversion_factor(s: Flow, t: Flow, data: dict) -> float | None:
            cf_data = data.get("conversion_factor")
            cf_s = s.conversion_factor
            if cf_data and cf_s:
                return cf_data * cf_s
            elif cf_data or cf_s:
                return cf_data or cf_s
            else:
                return s.unit.conversion_factor(t.unit)

        for target in target_flows:
            for rule in rules:
                is_match = rule(s=source, t=target, all_source_flows=source_flows, all_target_flows=target_flows)
                if is_match:
                    try:
                        return {
                            "from": source,
                            "to": target,
                            "conversion_factor": get_conversion_factor(
                                source, target, is_match
                            ),
                            "match_rule": rule.__name__,
                            "match_rule_priority": self.rules.index(rule),
                            "info": is_match,
                        }
                    except pint.errors.UndefinedUnitError:
                        warnings.warng(
                            f"Pint Units error converting source {source.export} to target {target.export}"
                        )
                        raise

    @cached_property
    def mappings(self):
        """
        Generates and returns a list of mappings from source flows to target flows based on the defined rules.

        Each mapping includes the source flow, target flow, conversion factor, the rule that determined the match, and additional information.

        A single match using the match rule with highest priority is returned for each source flow.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the mapping details.

        """
        results = [
            self.get_single_match(
                source=source, source_flows=self.source_flows, target_flows=self.target_flows, rules=self.rules
            )
            for source in tqdm(self.source_flows, disable=self.disable_progress)
        ]

        result, seen_sources, seen_combos = [], set(), {}
        for mapping in sorted([elem for elem in results if elem], key=match_sort_order):
            from_id = mapping["from"].uniqueness_id
            combo_key = (from_id, mapping["to"].uniqueness_id)
            if combo_key in seen_combos:
                other = seen_combos[combo_key]
                if (
                    isinstance(other["conversion_factor"], Number)
                    and isinstance(mapping["conversion_factor"], Number)
                    and not math.isclose(
                        other["conversion_factor"],
                        mapping["conversion_factor"],
                        1e-5,
                        1e-5,
                    )
                ):
                    raise DifferingConversions(
                        f"""
Found two different conversion factors for the same match from

{mapping['from']}

to

{mapping['to']}

Conversion factors:
    {other['match_rule']}: {other['conversion_factor']}
    {mapping['match_rule']}: {mapping['conversion_factor']}
"""
                    )
                elif not isinstance(other["conversion_factor"], Number) and isinstance(
                    mapping["conversion_factor"], Number
                ):
                    seen_combos[combo_key] = mapping
            elif from_id in seen_sources:
                other = next(
                    value for key, value in seen_combos.items() if key[0] == from_id
                )
                raise DifferingMatches(
                    f"""
{mapping['from']}

Matched to multiple targets, including:

Match rule: {mapping['match_rule']}:
{mapping['to']}

Match rule: {other['match_rule']}
{other['to']}
"""
                )
            else:
                seen_sources.add(from_id)
                seen_combos[combo_key] = mapping
                result.append(mapping)

        return result

    @cached_property
    def _matched_source_flows_ids(self):
        return {map_entry["from"].id for map_entry in self.mappings}

    @cached_property
    def _matched_target_flows_ids(self):
        return {map_entry["to"].id for map_entry in self.mappings}

    @cached_property
    def matched_source(self):
        """
        Provides a list of source flows that have been successfully matched to target flows.

        Returns
        -------
        list[Flow]
            A list of matched source flow objects.

        """
        result = [
            flow
            for flow in self.source_flows
            if flow.id in self._matched_source_flows_ids
        ]
        return result

    @cached_property
    def unmatched_source(self):
        """
        Provides a list of source flows that have not been matched to any target flows.

        Returns
        -------
        list[Flow]
            A list of unmatched source flow objects.

        """
        result = [
            flow
            for flow in self.source_flows
            if flow.id not in self._matched_source_flows_ids
        ]
        return result

    @cached_property
    def matched_source_statistics(self):
        """
        Calculates statistics for matched source flows, including the number of matches and the matching percentage for each context.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing matching statistics for source flows.

        """
        matched = Counter([flow.context.value for flow in self.matched_source])
        matched = pd.Series(matched).reset_index()
        matched.columns = ["context", "matched"]

        total = Counter([flow.context.value for flow in self.source_flows])
        total = pd.Series(total).reset_index()
        total.columns = ["context", "total"]

        df = pd.merge(matched, total, on="context", how="outer")
        df = df.fillna(0).astype({"matched": "int", "total": "int"})

        df["percent"] = df.matched / df.total
        result = df.sort_values("percent")
        return result

    @cached_property
    def matched_target(self):
        """
        Provides a list of target flows that have been successfully matched to source flows.

        Returns
        -------
        list[Flow]
            A list of matched target flow objects.

        """
        result = [
            flow
            for flow in self.target_flows
            if flow.id in self._matched_target_flows_ids
        ]
        return result

    @cached_property
    def unmatched_target(self):
        """
        Provides a list of target flows that have not been matched to any source flows.

        Returns
        -------
        list[Flow]
            A list of unmatched target flow objects.

        """
        result = [
            flow
            for flow in self.target_flows
            if flow.id not in self._matched_target_flows_ids
        ]
        return result

    @cached_property
    def matched_target_statistics(self):
        """
        Calculates statistics for matched target flows, including the number of matches and the matching percentage for each context.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing matching statistics for target flows.

        """
        matched = Counter([flow.context.value for flow in self.matched_target])
        matched = pd.Series(matched).reset_index()
        matched.columns = ["context", "matched"]

        total = Counter([flow.context.value for flow in self.target_flows])
        total = pd.Series(total).reset_index()
        total.columns = ["context", "total"]

        df = pd.merge(matched, total, on="context", how="outer")
        df = df.fillna(0).astype({"matched": "int", "total": "int"})

        df["percent"] = df.matched / df.total
        result = df.sort_values("percent")
        return result

    def statistics(self):
        """
        Prints out summary statistics for the flow mapping process.

        """
        source_msg = (
            f"{len(self.source_flows)} source flows ({len(self.source_flows_nomatch)} excluded)..."
            if self.source_flows_nomatch
            else f"{len(self.source_flows)} source flows..."
        )
        print(source_msg)
        target_msg = (
            f"{len(self.target_flows)} target flows ({len(self.target_flows_nomatch)} excluded)..."
            if self.target_flows_nomatch
            else f"{len(self.target_flows)} target flows..."
        )
        print(target_msg)
        print(
            f"{len(self.mappings)} mappings ({len(self.matched_source) / len(self.source_flows):.2%} of total)."
        )
        cardinalities = dict(Counter([x["cardinality"] for x in self._cardinalities]))
        print(f"Mappings cardinalities: {str(cardinalities)}")

    @cached_property
    def _cardinalities(self):
        """
        Calculates and returns the cardinalities of mappings between source and target flows.

        Returns
        -------
        list[dict]
            A sorted list of dictionaries, each indicating the cardinality relationship between a pair of source and target flows.

        """
        mappings = [
            (mapentry["from"].id, mapentry["to"].id) for mapentry in self.mappings
        ]
        lhs_counts = Counter([pair[0] for pair in mappings])
        rhs_counts = Counter([pair[1] for pair in mappings])

        result = []

        for lhs, rhs in mappings:
            lhs_count = lhs_counts[lhs]
            rhs_count = rhs_counts[rhs]
            if lhs_count == 1 and rhs_count == 1:
                result.append({"from": lhs, "to": rhs, "cardinality": "1:1"})
            elif lhs_count == 1 and rhs_count > 1:
                result.append({"from": lhs, "to": rhs, "cardinality": "N:1"})
            elif lhs_count > 1 and rhs_count == 1:
                result.append({"from": lhs, "to": rhs, "cardinality": "1:N"})
            elif lhs_count > 1 and rhs_count > 1:
                result.append({"from": lhs, "to": rhs, "cardinality": "N:M"})

        return sorted(result, key=lambda x: x["from"])

    def to_randonneur(
        self,
        source_id: str,
        target_id: str,
        contributors: list,
        mapping_source: dict,
        mapping_target: dict,
        version: str = "1.0.0",
        licenses: list | None = None,
        homepage: str | None = None,
        name: str | None = None,
        path: Path | None = None,
    ) -> randonneur.Datapackage:
        """
        Export mappings using randonneur data migration file format.

        Parameters
        ----------
        path : Path, optional
            If provided export the output file to disk.

        Returns
        -------
        randonneur.Datapackage object.

        """
        dp = randonneur.Datapackage(
            name=name or f"{source_id}-{target_id}",
            source_id=source_id,
            target_id=target_id,
            description=f"Flowmapper {__version__} elementary flow correspondence from {source_id} to {target_id}",
            contributors=contributors,
            mapping_source=mapping_source,
            mapping_target=mapping_target,
            homepage=homepage,
            version=version,
            licenses=licenses,
        )

        result = [
            format_match_result(
                map_entry["from"],
                map_entry["to"],
                map_entry["conversion_factor"],
                map_entry["info"],
            )
            for map_entry in self.mappings
        ]

        dp.add_data(verb="update", data=result)

        if path is not None:
            dp.to_json(path)
        return dp

    def to_glad(
        self,
        path: Path | None = None,
        ensure_id: bool = False,
        missing_source: bool = False,
    ):
        """
        Export mappings using GLAD flow mapping format, optionally ensuring each flow has an identifier.

        Formats the mapping results according to Global LCA Data Access (GLAD) network initiative flow mapping format.

        Parameters
        ----------
        path : Path, optional
            If provided export the output file to disk.
        ensure_id : bool, optional
            If True, ensures each flow has an identifier, default is False.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the formatted mapping results in GLAD format.

        """
        data = []
        for map_entry in self.mappings:
            data.append(
                {
                    "SourceFlowName": map_entry["from"].name.original,
                    "SourceFlowUUID": source_flow_id(
                        map_entry["from"], ensure_id=ensure_id
                    ),
                    "SourceFlowContext": map_entry["from"].context.export_as_string(),
                    "SourceUnit": map_entry["from"].unit.original,
                    "MatchCondition": "=",
                    "ConversionFactor": map_entry["conversion_factor"],
                    "TargetFlowName": map_entry["to"].name.original,
                    "TargetFlowUUID": map_entry["to"].identifier.original,
                    "TargetFlowContext": map_entry["to"].context.export_as_string(),
                    "TargetUnit": map_entry["to"].unit.original,
                    "MemoMapper": map_entry["info"].get("comment"),
                }
            )

        if missing_source:
            for flow_obj in self.unmatched_source:
                data.append(
                    {
                        "SourceFlowName": flow_obj.name.original,
                        "SourceFlowUUID": source_flow_id(flow_obj, ensure_id=ensure_id),
                        "SourceFlowContext": flow_obj.context.export_as_string(),
                        "SourceUnit": flow_obj.unit.original,
                    }
                )

        result = pd.DataFrame(data)

        if not path:
            return result
        else:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)

            writer = pd.ExcelWriter(
                path,
                engine="xlsxwriter",
                engine_kwargs={"options": {"strings_to_formulas": False}},
            )
            result.to_excel(writer, sheet_name="Mapping", index=False, na_rep="NaN")

            for column in result:
                column_length = max(
                    result[column].astype(str).map(len).max(), len(column)
                )
                col_idx = result.columns.get_loc(column)
                writer.sheets["Mapping"].set_column(col_idx, col_idx, column_length)

            writer.close()
