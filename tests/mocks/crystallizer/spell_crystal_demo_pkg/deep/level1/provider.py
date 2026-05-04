"""
Deep level-1 dependency for `SpellCrystal` physical-graph tests.
"""

from .level2.provider import DeepLevelDependency


class Level1Dependency:
    """
    Intermediate dependency with a transitive import.
    """

    deep_type = DeepLevelDependency
