"""
Branch aggregate dependency for `SpellCrystal` physical-graph tests.
"""

from .leaf_a import BranchLeafA
from .leaf_b import BranchLeafB


class AggregateDependency:
    """
    Aggregate dependency with two branch-leaf transitive imports.
    """

    leaf_a_type = BranchLeafA
    leaf_b_type = BranchLeafB
