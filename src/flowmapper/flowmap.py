from collections import Counter
from collections.abc import Callable
from functools import cached_property
from pathlib import Path
from time import time

import pandas as pd
import randonneur
from structlog import get_logger

from flowmapper import __version__
from flowmapper.domain.flow import Flow
from flowmapper.domain.match import Match
from flowmapper.domain.normalized_flow import NormalizedFlow
from flowmapper.matching import match_rules
from flowmapper.utils import apply_transformation_and_convert_flows_to_normalized_flows

logger = get_logger("flowmapper")


class Flowmap:
    """
    Crosswalk of flows from a source flow list to a target flow list.

    The Flowmap class manages the mapping process between source and target flow lists
    using a series of matching rules. It tracks matches, generates statistics, and
    provides export functionality for various formats (randonneur, GLAD).

    The class applies matching rules sequentially to find correspondences between
    source and target flows. As matches are found, source flows are marked as matched
    and excluded from subsequent rule applications. New target flows can be created
    during the matching process and added to the target flow list.

    Attributes
    ----------
    source_flows : list[NormalizedFlow]
        The list of source flows to be mapped. These flows are checked against
        matching rules to find correspondences with target flows.
    target_flows : list[NormalizedFlow]
        The list of target flows for mapping. This list can grow during matching
        if new target flows are created by matching rules.
    matches : list[Match]
        List of Match objects representing successful mappings between source
        and target flows. Initially empty, populated by `generate_matches()`.
    rules : list[Callable[..., list[Match]]]
        List of matching rule functions to apply. Each rule is a callable that
        takes source_flows and target_flows and returns a list of Match objects.
    data_preparation_functions : list[Callable[..., list[NormalizedFlow]]]
        List of transformation functions used to prepare flows for matching and
        to normalize newly created target flows.
    show_progressbar : bool
        Whether to display a progress bar during matching (currently not used).

    Examples
    --------
    >>> from flowmapper.domain.flow import Flow
    >>> from flowmapper.domain.normalized_flow import NormalizedFlow
    >>> from flowmapper.flowmap import Flowmap
    >>> from copy import copy
    >>>
    >>> # Create source and target flows
    >>> source_flow = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> source_nf = NormalizedFlow(
    ...     original=source_flow,
    ...     normalized=source_flow.normalize(),
    ...     current=copy(source_flow.normalize())
    ... )
    >>>
    >>> target_flow = Flow.from_dict({
    ...     "name": "Carbon dioxide",
    ...     "context": "air",
    ...     "unit": "kg"
    ... })
    >>> target_nf = NormalizedFlow(
    ...     original=target_flow,
    ...     normalized=target_flow.normalize(),
    ...     current=copy(target_flow.normalize())
    ... )
    >>>
    >>> # Create Flowmap and generate matches
    >>> flowmap = Flowmap(
    ...     source_flows=[source_nf],
    ...     target_flows=[target_nf],
    ...     data_preparation_functions=[]
    ... )
    >>> flowmap.generate_matches()
    >>> len(flowmap.matches)
    1
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
        Initialize a Flowmap with source and target flows.

        Creates a new Flowmap instance to manage the mapping process between
        source and target flow lists. The matching rules and data preparation
        functions are set up for use during the matching process.

        Parameters
        ----------
        source_flows : list[NormalizedFlow]
            The list of source flows to be mapped. These flows will be checked
            against matching rules to find correspondences with target flows.
        target_flows : list[NormalizedFlow]
            The list of target flows for mapping. This list can grow during
            matching if new target flows are created.
        data_preparation_functions : list[Callable[..., list[NormalizedFlow]]]
            List of transformation functions used to prepare flows for matching.
            These functions are also used to normalize newly created target flows
            when they are added via `add_new_target_flows()`.
        rules : list[Callable[..., list[Match]]] | None, optional
            Custom matching rules to use. Each rule is a callable that takes
            `source_flows` and `target_flows` as arguments and returns a list
            of Match objects. If None, defaults to the rules returned by
            `match_rules()`.
        show_progressbar : bool, default=True
            Whether to show a progress bar during matching (currently not
            implemented).

        Notes
        -----
        - The `matches` list is initialized as empty and populated by calling
          `generate_matches()`.
        - Source flows are filtered by their `matched` attribute during rule
          application, so only unmatched flows are passed to each rule.
        - New target flows created during matching are automatically normalized
          using the data preparation functions before being added to the target
          flow list.

        Examples
        --------
        >>> from flowmapper.flowmap import Flowmap
        >>> from flowmapper.matching import match_rules
        >>>
        >>> flowmap = Flowmap(
        ...     source_flows=[source_nf1, source_nf2],
        ...     target_flows=[target_nf1, target_nf2],
        ...     data_preparation_functions=[],
        ...     rules=match_rules()
        ... )
        """
        self.show_progressbar = show_progressbar
        self.rules = rules if rules else match_rules()
        self.data_preparation_functions = data_preparation_functions
        self.source_flows = source_flows
        self.target_flows = target_flows
        self.matches = []

    @cached_property
    def _matched_source_flows_ids(self) -> set[int]:
        """Get a set of source flow IDs that have been matched.

        Returns
        -------
        set[int]
            Set of internal IDs (_id) from source flows that appear in matches.
            Empty set if no matches exist.

        Notes
        -----
        - This is a cached property used internally by `matched_source()` and
          `unmatched_source` to efficiently determine which flows have been matched
        - The cache is invalidated when `matches` changes
        """
        return {match.source._id for match in self.matches}

    def generate_matches(self) -> None:
        """Generate matches by applying all matching rules sequentially.

        This method iterates through all matching rules and applies them to
        find correspondences between source and target flows. For each rule:
        1. Filters source flows to only include unmatched flows
        2. Calls the rule function with unmatched source flows and all target flows
        3. Extends the matches list with results from the rule
        4. If any matches create new target flows, adds them to the target flow list
        5. Logs the number of matches found and time taken

        After this method completes, the `matches` list contains all matches
        found by all rules, and source flows that were matched will have their
        `matched` attribute set to True.

        Notes
        -----
        - Rules are applied in the order they appear in `self.rules`
        - Each rule only receives source flows that haven't been matched yet
        - New target flows are automatically normalized before being added
        - The method logs information about each rule's performance

        Examples
        --------
        >>> flowmap = Flowmap(
        ...     source_flows=[source_nf],
        ...     target_flows=[target_nf],
        ...     data_preparation_functions=[]
        ... )
        >>> flowmap.generate_matches()
        >>> len(flowmap.matches)
        1
        """
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
        """Add new target flows to the target flow list.

        This method is called automatically by `generate_matches()` when a
        matching rule creates new target flows (indicated by `new_target_flow=True`
        in Match objects). The new flows are normalized using the data
        preparation functions before being added to the target flow list.

        Parameters
        ----------
        flows : list[Flow]
            List of Flow objects to add as new target flows. These flows are
            normalized using `data_preparation_functions` before being added.

        Notes
        -----
        - The flows are normalized using `apply_transformation_and_convert_flows_to_normalized_flows`
        - Normalized flows are appended to `self.target_flows`
        - This method is typically called automatically during `generate_matches()`

        Examples
        --------
        >>> new_flow = Flow.from_dict({
        ...     "name": "New flow",
        ...     "context": "air",
        ...     "unit": "kg"
        ... })
        >>> flowmap.add_new_target_flows([new_flow])
        >>> len(flowmap.target_flows)
        2
        """
        normalized_flows = apply_transformation_and_convert_flows_to_normalized_flows(
            functions=self.data_preparation_functions, flows=flows
        )
        self.target_flows.extend(normalized_flows)

    def matched_source(self) -> list[NormalizedFlow]:
        """Get a list of source flows that have been successfully matched.

        Returns all source flows that have been matched to at least one target
        flow. A source flow is considered matched if its ID appears in any
        Match object in the `matches` list.

        Returns
        -------
        list[NormalizedFlow]
            List of NormalizedFlow objects that have been matched. The list
            is empty if no matches have been generated yet.

        Notes
        -----
        - Uses the `_matched_source_flows_ids` cached property to determine
          which flows have been matched
        - Returns flows in the same order as they appear in `source_flows`
        - Call `generate_matches()` first to populate matches

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> matched = flowmap.matched_source()
        >>> len(matched)
        1
        >>> matched[0].matched
        True
        """
        result = [
            flow
            for flow in self.source_flows
            if flow.id in self._matched_source_flows_ids
        ]
        return result

    @cached_property
    def unmatched_source(self) -> list[NormalizedFlow]:
        """Get a list of source flows that have not been matched.

        Returns all source flows that have not been matched to any target flow.
        A source flow is considered unmatched if its ID does not appear in any
        Match object in the `matches` list.

        Returns
        -------
        list[NormalizedFlow]
            List of NormalizedFlow objects that have not been matched. Returns
            all source flows if no matches have been generated yet.

        Notes
        -----
        - This is a cached property, so it's computed once and cached
        - Uses the `_matched_source_flows_ids` cached property to determine
          which flows have been matched
        - Returns flows in the same order as they appear in `source_flows`
        - The cache is invalidated if the `matches` list changes

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> unmatched = flowmap.unmatched_source
        >>> len(unmatched)
        0
        """
        result = [
            flow
            for flow in self.source_flows
            if flow.id not in self._matched_source_flows_ids
        ]
        return result

    def matched_source_statistics(self) -> pd.DataFrame:
        """Calculate matching statistics grouped by source flow context.

        Computes statistics showing how many source flows were matched for each
        context, including the total number of source flows per context and
        the matching percentage.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            - `context`: The context value
            - `matched`: Number of matches for this context
            - `total`: Total number of source flows in this context
            - `percent`: Matching percentage (matched / total)
            Rows are sorted by matching percentage (ascending).

        Notes
        -----
        - Contexts with no matches will have `matched=0`
        - Contexts with no source flows will have `total=0`
        - Percentages are calculated as matched/total, which may be > 1.0 if
          multiple matches exist per source flow
        - Results are sorted by percentage (lowest first)

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> stats = flowmap.matched_source_statistics()
        >>> stats.columns.tolist()
        ['context', 'matched', 'total', 'percent']
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
    def matched_target_statistics(self) -> pd.DataFrame:
        """Calculate matching statistics grouped by target flow context.

        Computes statistics showing how many target flows were matched for each
        context, including the total number of target flows per context and
        the matching percentage.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            - `context`: The context value
            - `matched`: Number of matches for this context
            - `total`: Total number of target flows in this context
            - `percent`: Matching percentage (matched / total)
            Rows are sorted by matching percentage (ascending).

        Notes
        -----
        - This is a cached property, so it's computed once and cached
        - Contexts with no matches will have `matched=0`
        - Contexts with no target flows will have `total=0`
        - Percentages are calculated as matched/total, which may be > 1.0 if
          multiple matches exist per target flow
        - Results are sorted by percentage (lowest first)
        - The cache is invalidated if the `matches` or `target_flows` lists change

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> stats = flowmap.matched_target_statistics
        >>> stats.columns.tolist()
        ['context', 'matched', 'total', 'percent']
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

    def print_statistics(self) -> None:
        """Print summary statistics for the flow mapping process.

        Displays a formatted summary including:
        - Number of source and target flows
        - Total number of matches and percentage of source flows matched
        - Cardinality distribution of mappings (1:1, 1:N, N:1, N:M)

        The output is printed to stdout in a human-readable format.

        Notes
        -----
        - Percentage is calculated as matches / source_flows
        - Cardinalities are computed by `cardinalities()` method
        - This method prints to stdout, so it's suitable for interactive use
          but may need to be captured or redirected in automated contexts

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> flowmap.print_statistics()
        1 source and 1 target flows.
        1 mappings (100.00% of total).
        Mappings cardinalities: {'1:1': 1}
        """
        cardinalities = dict(Counter([x["cardinality"] for x in self.cardinalities()]))
        percentage = (
            len(self.matches) / len(self.source_flows) if self.source_flows else 0.0
        )
        print(
            f"""{len(self.source_flows)} source and {len(self.target_flows)} target flows.
{len(self.matches)} mappings ({percentage:.2%} of total).
Mappings cardinalities: {str(cardinalities)}"""
        )

    def cardinalities(self) -> list[dict[str, int | str]]:
        """Calculate and return the cardinality of each mapping.

        Determines the relationship type (1:1, 1:N, N:1, or N:M) for each
        match based on how many matches each source and target flow participate in.

        Returns
        -------
        list[dict[str, int | str]]
            List of dictionaries, each containing:
            - `from`: Source flow internal ID
            - `to`: Target flow internal ID
            - `cardinality`: Relationship type as string ("1:1", "1:N", "N:1", or "N:M")
            Results are sorted by source flow ID.

        Notes
        -----
        - **1:1**: One source maps to one target, and that target maps only to this source
        - **1:N**: One source maps to multiple targets
        - **N:1**: Multiple sources map to the same target
        - **N:M**: Multiple sources map to multiple targets (many-to-many)
        - Cardinality is determined by counting how many matches each source
          and target flow ID appears in

        Examples
        --------
        >>> flowmap.generate_matches()
        >>> card = flowmap.cardinalities()
        >>> card[0]
        {'from': 0, 'to': 0, 'cardinality': '1:1'}
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
        """Export mappings in randonneur data migration format.

        Creates a randonneur Datapackage containing all matches in a format
        suitable for data migration and transformation workflows. The datapackage
        can be saved to disk or returned for further processing.

        Parameters
        ----------
        source_id : str
            Identifier for the source flow list (e.g., "ecoinvent-3.8").
        target_id : str
            Identifier for the target flow list (e.g., "ecoinvent-3.9").
        contributors : list
            List of contributor information for the datapackage metadata.
        mapping_source : dict
            Mapping configuration for source flows (randonneur format).
        mapping_target : dict
            Mapping configuration for target flows (randonneur format).
        version : str, default="1.0.0"
            Version string for the datapackage.
        licenses : list | None, optional
            License information for the datapackage.
        homepage : str | None, optional
            Homepage URL for the datapackage.
        name : str | None, optional
            Name for the datapackage. If None, defaults to "{source_id}-{target_id}".
        path : Path | None, optional
            If provided, saves the datapackage as JSON to this path.

        Returns
        -------
        randonneur.Datapackage
            A Datapackage object containing all matches with verb "update".
            The datapackage includes metadata and can be saved to disk if
            `path` is provided.

        Notes
        -----
        - All matches are exported using their `export()` method
        - The datapackage description includes the flowmapper version
        - If `path` is provided, the parent directory is created if it doesn't exist

        Examples
        --------
        >>> dp = flowmap.to_randonneur(
        ...     source_id="source-v1",
        ...     target_id="target-v1",
        ...     contributors=[],
        ...     mapping_source={},
        ...     mapping_target={}
        ... )
        >>> isinstance(dp, randonneur.Datapackage)
        True
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
    ) -> pd.DataFrame | None:
        """Export mappings in GLAD (Global LCA Data Access) format.

        Creates a DataFrame or Excel file in the GLAD flow mapping format,
        which is a standardized format for exchanging flow mappings in the
        LCA community.

        Parameters
        ----------
        path : Path | None, optional
            If provided, exports the DataFrame to an Excel file at this path.
            If None, returns the DataFrame without saving.
        ensure_id : bool, default=False
            If True, replaces None identifiers with empty strings. If False,
            None identifiers remain as None in the DataFrame.
        missing_source : bool, default=False
            If True, includes unmatched source flows in the output with only
            source flow information (no target flow data).

        Returns
        -------
        pd.DataFrame | None
            DataFrame with GLAD format columns:
            - SourceFlowName, SourceFlowUUID, SourceFlowContext, SourceUnit
            - MatchCondition, ConversionFactor
            - TargetFlowName, TargetFlowUUID, TargetFlowContext, TargetUnit
            - MemoMapper
            Returns None if `path` is provided (file is saved instead).

        Notes
        -----
        - If `path` is provided, creates an Excel file with auto-sized columns
        - Unmatched source flows (when `missing_source=True`) only include
          source flow columns, with target columns left empty
        - Context values are exported as strings using "/" as separator
        - Match conditions are converted using `MatchCondition.as_glad()`
        - Excel files use xlsxwriter engine with formulas disabled

        Examples
        --------
        >>> df = flowmap.to_glad()
        >>> df.columns.tolist()
        ['SourceFlowName', 'SourceFlowUUID', ...]
        >>>
        >>> # Export to Excel
        >>> flowmap.to_glad(path=Path("mapping.xlsx"))
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
