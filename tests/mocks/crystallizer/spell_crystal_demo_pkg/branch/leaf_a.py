"""
Branch leaf A for `SpellCrystal` physical-graph tests.
"""


class BranchLeafA:
    """
    Simple branch leaf dependency used by test-only module graphs.
    """

    def read(self) -> str:
        """
        Return one stable marker string.
        """
        return "branch_a"
