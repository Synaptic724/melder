"""
Deep level-2 leaf dependency for `SpellCrystal` physical-graph tests.
"""


class DeepLevelDependency:
    """
    Deep leaf dependency used by test-only module graphs.
    """

    def read(self) -> str:
        """
        Return one stable marker string.
        """
        return "deep"
