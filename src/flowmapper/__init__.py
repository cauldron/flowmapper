__all__ = (
    "__version__",
    "CASField",
    "ContextField",
    "Flow",
    "Flowmap",
    "flowmapper",
    "Match",
    "MatchCondition",
    "NormalizedFlow",
    "UnitField",
)

__version__ = "0.4.2"

from flowmapper.domain import Flow, Match, MatchCondition, NormalizedFlow
from flowmapper.fields import CASField, ContextField
from flowmapper.flowmap import Flowmap
from flowmapper.main import flowmapper
from flowmapper.unit import UnitField
