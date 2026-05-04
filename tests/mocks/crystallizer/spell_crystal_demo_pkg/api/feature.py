"""
API feature dependency for `SpellCrystal` physical-graph tests.
"""

from ..deep.level1.provider import Level1Dependency
from ..shared import SharedDependency


class ApiFeatureDependency:
    """
    API feature dependency with shared and deep transitive imports.
    """

    shared_type = SharedDependency
    level1_type = Level1Dependency
