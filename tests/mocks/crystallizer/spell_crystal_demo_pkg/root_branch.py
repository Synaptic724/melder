"""
Branch-root module used by `SpellCrystal` physical-graph tests.
"""

from .branch.aggregate import AggregateDependency
from .shared import SharedDependency


class BranchRootService:
    """
    Root service with one shared and one branching dependency.
    """

    shared_type = SharedDependency
    aggregate_type = AggregateDependency
