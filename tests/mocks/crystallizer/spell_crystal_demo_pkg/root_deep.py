"""
Deep-root module used by `SpellCrystal` physical-graph tests.
"""

from .deep.level1.provider import Level1Dependency
from .shared import SharedDependency


class DeepRootService:
    """
    Root service with one shared and one deep transitive dependency.
    """

    shared_type = SharedDependency
    level1_type = Level1Dependency
