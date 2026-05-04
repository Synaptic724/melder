"""
API surface dependency for `SpellCrystal` physical-graph tests.
"""

from .feature import ApiFeatureDependency


class ApiSurfaceDependency:
    """
    API surface dependency that reuses the feature dependency.
    """

    feature_type = ApiFeatureDependency
