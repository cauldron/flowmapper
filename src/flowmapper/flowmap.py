from collections import Counter
from collections.abc import Callable
from functools import cached_property
from pathlib import Path
from time import time

import pandas as pd
import randonneur
from structlog import get_logger

from flowmapper import __version__
from flowmapper.domain import Flow, Match, NormalizedFlow
from flowmapper.matching import match_rules
from flowmapper.utils import apply_generic_transformations_to_flows

logger = get_logger("flowmapper")


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
        source_flows: list[NormalizedFlow],
        target_flows: list[NormalizedFlow],
        data_preparation_functions: list[Callable[..., list[NormalizedFlow]]],
        rules: list[Callable[..., list[Match]]] | None = None,
        show_progressbar: bool = True,
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
        show_progressbar : bool, optional
            If False, progress bar display during the mapping process is disabled.

        """
        self.show_progressbar = show_progressbar
        self.rules = rules if rules else match_rules()
        self.data_preparation_functions = data_preparation_functions
        self.source_flows = source_flows
        self.target_flows = target_flows
        self.matches = []

    def generate_matches(self) -> None:
        """Generate matches by applying match rules"""
        for rule in self.rules:
            start = time()
            result = rule(
                source_flows=[flow for flow in self.source_flows if not flow.matched],
                target_flows=self.target_flows,
            )
            elapsed = time() - start

            if new_target_flows := [
                obj.target for obj in result if obj.new_target_flow
            ]:
                self.add_new_target_flows(new_target_flows)
                logger.info(
                    f"Match function {rule.__name__} produced {len(result)} matches and added {len(new_target_flows)} new target flows. It took {elapsed:.3} seconds."
                )
            else:
                logger.info(
                    f"Match function {rule.__name__} produced {len(result)} matches. It took {elapsed:.3} seconds."
                )
            self.matches.extend(result)

    def add_new_target_flows(self, flows: list[Flow]) -> None:
        normalized_flows = apply_generic_transformations_to_flows(
            functions=self.data_preparation_functions, flows=flows
        )
        self.target_flows.extend(normalized_flows)

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

    def matched_source_statistics(self):
        """
        Calculates statistics for matched source flows, including the number of matches and the matching percentage for each context.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing matching statistics for source flows.

        """
        matched = pd.Series(
            Counter([flow.source.context.value for flow in self.matches])
        ).reset_index()
        matched.columns = ["context", "matched"]

        total = pd.Series(
            Counter([flow.original.context.value for flow in self.source_flows])
        ).reset_index()
        total.columns = ["context", "total"]

        df = pd.merge(matched, total, on="context", how="outer")
        df = df.fillna(0).astype({"matched": "int", "total": "int"})

        df["percent"] = df.matched / df.total
        result = df.sort_values("percent")
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
        matched = pd.Series(
            Counter([flow.target.context.value for flow in self.matches])
        ).reset_index()
        matched.columns = ["context", "matched"]

        total = pd.Series(
            Counter([flow.original.context.value for flow in self.target_flows])
        ).reset_index()
        total.columns = ["context", "total"]

        df = pd.merge(matched, total, on="context", how="outer")
        df = df.fillna(0).astype({"matched": "int", "total": "int"})

        df["percent"] = df.matched / df.total
        result = df.sort_values("percent")
        return result

    def print_statistics(self):
        """
        Prints out summary statistics for the flow mapping process.

        """
        cardinalities = dict(Counter([x["cardinality"] for x in self.cardinalities()]))
        print(
            f"""{len(self.source_flows)} source and {len(self.target_flows)} target flows.
{len(self.matches)} mappings ({len(self.matches) / len(self.source_flows):.2%} of total).
Mappings cardinalities: {str(cardinalities)}"""
        )

    def cardinalities(self):
        """
        Calculates and returns the cardinalities of mappings between source and target flows.

        Returns
        -------
        list[dict]
            A sorted list of dictionaries, each indicating the cardinality relationship between a pair of source and target flows.

        """
        mappings = [(match.source._id, match.target._id) for match in self.matches]
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

        dp.add_data(verb="update", data=[match.export() for match in self.matches])

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
        for match in self.matches:
            data.append(
                {
                    "SourceFlowName": str(match.source.name),
                    "SourceFlowUUID": match.source.identifier
                    or ("" if ensure_id else None),
                    "SourceFlowContext": match.source.context.export_as_string(
                        join_character="/"
                    ),
                    "SourceUnit": str(match.source.unit),
                    "MatchCondition": match.condition.as_glad(),
                    "ConversionFactor": match.conversion_factor,
                    "TargetFlowName": str(match.target.name),
                    "TargetFlowUUID": match.target.identifier
                    or ("" if ensure_id else None),
                    "TargetFlowContext": match.target.context.export_as_string(
                        join_character="/"
                    ),
                    "TargetUnit": str(match.target.unit),
                    "MemoMapper": match.comment,
                }
            )

        if missing_source:
            for flow_obj in filter(lambda x: not x.matched, self.source_flows):
                data.append(
                    {
                        "SourceFlowName": str(flow_obj.original.name),
                        "SourceFlowUUID": flow_obj.original.identifier
                        or ("" if ensure_id else None),
                        "SourceFlowContext": flow_obj.original.context.export_as_string(),
                        "SourceUnit": str(flow_obj.original.unit),
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
