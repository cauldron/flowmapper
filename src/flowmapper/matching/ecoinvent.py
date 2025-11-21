from functools import partial

from flowmapper.domain.match_condition import MatchCondition
from flowmapper.matching.basic import match_identical_names
from flowmapper.matching.core import transform_and_then_match
from flowmapper.utils import apply_randonneur

match_ecoinvent_transitive_matching = partial(
    transform_and_then_match,
    match_function=partial(
        match_identical_names,
        function_name="match_ecoinvent_transitive_matching",
        comment="Shared normalized attributes after applying transformation: ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive",
        match_condition=MatchCondition.close,
    ),
    transform_source_flows=[
        partial(
            apply_randonneur,
            datapackage="ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive",
            fields=["name", "context"],
        )
    ],
    transform_target_flows=[
        partial(
            apply_randonneur,
            datapackage="ecoinvent-2.2-biosphere-ecoinvent-3.12-biosphere-transitive",
            fields=["name", "context"],
        )
    ],
)
match_ecoinvent_transitive_matching.__name__ = "match_ecoinvent_transitive_matching"
