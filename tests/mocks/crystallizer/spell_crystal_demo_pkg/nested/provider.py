"""
Nested provider dependency module for `SpellCrystal` tests.
"""


class NestedDependency:
    """
    Simple nested dependency class used by test-only module graphs.
    """

    def read(self) -> str:
        """
        Return one stable marker string.
        """
        return "nested"
