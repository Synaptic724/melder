"""
Multi-branch root used by `SpellCrystal` physical-graph tests.
"""

from .branch.aggregate import AggregateDependency
from .nested.provider import NestedDependency
from .shared import SharedDependency


class MultiBranchRootService:
    """
    Root service with shared, nested, and branching dependencies together.
    """

    shared_type = SharedDependency
    nested_type = NestedDependency
    aggregate_type = AggregateDependency
