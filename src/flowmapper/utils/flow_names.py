"""Flow name processing utility functions."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from flowmapper.domain.flow import Flow

logger = structlog.get_logger("flowmapper")

unit_slash = re.compile(r"/(?P<unit>m3|kg)(\,?\s+|\s+|$)")


def remove_unit_slash(obj: Flow) -> str:
    """Remove unit references from flow names that appear as '/unit' suffix."""
    name = obj.name.data
    if match := unit_slash.search(name):
        obj_dict = match.groupdict()
        if match.end() == len(name):
            name = name[: match.start()]
        else:
            name = name[: match.start()] + ", " + name[match.end() :]
        if not obj.unit.compatible(obj_dict["unit"]):
            logger.warning(
                f"Flow {obj} has unit '{obj.unit}' but name refers to incompatible unit '{obj_dict['unit']}'"
            )
    return name
