"""
Package-import root used by `SpellCrystal` physical-graph tests.
"""

from .nested import provider


class PackageImportRootService:
    """
    Root service that imports a package and then uses the provider submodule.
    """

    nested_type = provider.NestedDependency
