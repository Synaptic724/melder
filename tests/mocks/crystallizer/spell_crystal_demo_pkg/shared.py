"""
Shared dependency module for `SpellCrystal` physical-graph tests.
"""


class SharedDependency:
    """
    Simple shared dependency class used by test-only module graphs.
    """

    def read(self) -> str:
        """
        Return one stable marker string.
        """
        return "shared"
