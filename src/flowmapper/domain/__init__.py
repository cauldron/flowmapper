"""Domain entities for flowmapper.

This package contains the core domain model classes:
- Flow: Represents an elementary flow with all its attributes
- NormalizedFlow: Manages flow transformations and matching state
- Match: Represents a mapping between source and target flows
- MatchCondition: Enumeration of match quality levels
"""

from flowmapper.domain.flow import Flow
from flowmapper.domain.match import Match
from flowmapper.domain.match_condition import MatchCondition
from flowmapper.domain.normalized_flow import NormalizedFlow

__all__ = ["Flow", "NormalizedFlow", "Match", "MatchCondition"]
