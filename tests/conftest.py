"""Fixtures for flowmapper"""

import pytest

from flowmapper.domain import Flow
from flowmapper.transformation_mapping import prepare_transformations
from flowmapper.utils import (
    apply_transformations,
    load_standard_transformations,
    read_migration_files,
)


@pytest.fixture
def transformations():
    return prepare_transformations(load_standard_transformations())
