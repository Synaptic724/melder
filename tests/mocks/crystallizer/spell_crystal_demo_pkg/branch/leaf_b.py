"""
Branch leaf B for `SpellCrystal` physical-graph tests.
"""


class BranchLeafB:
    """
    Simple branch leaf dependency used by test-only module graphs.
    """

    def read(self) -> str:
        """
        Return one stable marker string.
        """
        return "branch_b"
