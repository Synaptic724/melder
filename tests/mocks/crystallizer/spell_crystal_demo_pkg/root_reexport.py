"""
Re-export-root module used by `SpellCrystal` physical-graph tests.
"""

from .nested.reexport import ReexportedNestedDependency
from .shared import SharedDependency


class ReexportRootService:
    """
    Root service that depends on a re-export surface and one shared module.
    """

    shared_type = SharedDependency
    nested_type = ReexportedNestedDependency
