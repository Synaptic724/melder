"""
API-surface root used by `SpellCrystal` physical-graph tests.
"""

from .api.surface import ApiSurfaceDependency


class ApiSurfaceRootService:
    """
    Root service that starts from the API surface dependency.
    """

    surface_type = ApiSurfaceDependency
