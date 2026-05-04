"""
Duplicate-import root used by `SpellCrystal` physical-graph tests.
"""

from .shared import SharedDependency
from .shared import SharedDependency as SharedDependencyAlias
import tests.mocks.crystallizer.spell_crystal_demo_pkg.shared as shared_mod


class DuplicateImportRootService:
    """
    Root service that imports the same module through multiple syntax forms.
    """

    shared_type = SharedDependency
    shared_alias_type = SharedDependencyAlias
    shared_module = shared_mod
